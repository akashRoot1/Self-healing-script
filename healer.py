import re
import difflib
import logging
from typing import Optional

logger = logging.getLogger("healer")
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)

class SelfHealer:
    # FIXED: removed quotes inside to avoid SyntaxError
    INTERACTIVE_CSS = "button, a, input, select, textarea, [role=button], [role=link], [role=tab], [type=submit], [type=button]"

    def __init__(self, model: str = "llama3.2", max_candidates: int = 25):
        self.model = model
        self.max_candidates = max_candidates
        self.cache: dict[str, str] = {}
        self.heal_count = 0

    async def smart_click(self, page, selector: str, intent: str, **kw):
        loc = await self._resolve(page, selector, intent)
        if loc is None:
            raise RuntimeError(f"❌ Could not heal locator for: {intent}")
        await loc.click(**kw)
        logger.info(f" Clicked: {intent}")

    async def smart_fill(self, page, selector: str, intent: str, value: str, **kw):
        loc = await self._resolve(page, selector, intent)
        if loc is None:
            raise RuntimeError(f"❌ Could not heal locator for: {intent}")
        await loc.fill(value, **kw)
        logger.info(f" Filled '{value}' into: {intent}")

    async def _resolve(self, page, selector: str, intent: str):
        try:
            loc = page.locator(selector).first
            if await loc.count() > 0:
                return loc
        except Exception:
            pass

        logger.info(f"  Original locator failed: {selector}")
        logger.info(f"   Intent: {intent}")

        if intent in self.cache:
            cached = self.cache[intent]
            try:
                loc = self._safe_eval(page, cached)
                if await loc.count() > 0:
                    logger.info(f"  Cache hit: {cached}")
                    return loc.first
            except Exception:
                del self.cache[intent]

        candidates = await self._extract_candidates(page)
        if not candidates:
            logger.warning("No candidates found on page")
            return None

        logger.info(f"Found {len(candidates)} interactive elements on page")

        llm_loc = await self._ask_ollama(intent, selector, candidates)
        if llm_loc:
            try:
                loc = self._safe_eval(page, llm_loc)
                if await loc.count() > 0:
                    self.cache[intent] = llm_loc
                    self.heal_count += 1
                    logger.info(f" LLM healed → {llm_loc}")
                    return loc.first
            except Exception as e:
                logger.warning(f"LLM suggestion invalid: {e}")

        fuzzy_loc = self._fuzzy_heal(intent, candidates)
        if fuzzy_loc:
            try:
                loc = self._safe_eval(page, fuzzy_loc)
                if await loc.count() > 0:
                    self.cache[intent] = fuzzy_loc
                    self.heal_count += 1
                    logger.info(f" Fuzzy healed → {fuzzy_loc}")
                    return loc.first
            except Exception:
                pass
        return None

    # FIXED METHOD - this was crashing before
    async def _extract_candidates(self, page) -> list[dict]:
        js = """
        (args) => {
            const selector = args.selector;
            const max = args.max;
            const els = Array.from(document.querySelectorAll(selector));
            return els.slice(0, max).map((el, i) => {
                const r = el.getBoundingClientRect();
                return {
                    index: i,
                    tag: el.tagName.toLowerCase(),
                    text: (el.innerText || el.value || '').trim().slice(0, 80),
                    id: el.id || '',
                    name: el.getAttribute('name') || '',
                    type: el.getAttribute('type') || '',
                    role: el.getAttribute('role') || '',
                    class: (el.className || '').toString().slice(0, 80),
                    data_testid: el.getAttribute('data-testid') || el.getAttribute('data-test') || '',
                    placeholder: el.getAttribute('placeholder') || '',
                    aria_label: el.getAttribute('aria-label') || '',
                    href: el.getAttribute('href') || '',
                    visible: r.width > 0 && r.height > 0
                };
            }).filter(c => c.visible && (
                c.text || c.id || c.data_testid ||
                c.name || c.placeholder || c.aria_label
            ));
        }
        """
        try:
            return await page.evaluate(js, {"selector": self.INTERACTIVE_CSS, "max": self.max_candidates})
        except Exception as e:
            logger.warning(f"Candidate extraction failed: {e}")
            return []

    async def _ask_ollama(self, intent: str, original: str, candidates: list[dict]) -> Optional[str]:
        try:
            import ollama as ollama_client
        except ImportError:
            return None
        cands_text = ""
        for c in candidates:
            parts = [f"[{c['index']}] <{c['tag']}>"]
            for key, label in [("text","text"),("id","id"),("data_testid","data-testid"),("name","name"),("role","role"),("placeholder","placeholder"),("aria_label","aria-label")]:
                val = c.get(key, "")
                if val:
                    parts.append(f'{label}="{val[:50]}"')
            cands_text += "  " + " | ".join(parts) + "\n"

        prompt = f"""You are a test automation expert.
BROKEN: {original}
INTENT: "{intent}"
ELEMENTS:
{cands_text}
Pick best match. Reply with:
LOCATOR: <Playwright locator like get_by_role("button", name="Publish") or locator("[data-testid='btn-primary']")>
"""
        try:
            response = ollama_client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.1, "num_predict": 200}
            )
            raw = response["message"]["content"].strip()
            m = re.search(r"LOCATOR:\s*(.+)", raw, re.IGNORECASE)
            if m:
                loc = m.group(1).strip().strip('"').strip("'").strip("`")
                loc = loc.replace("“", '"').replace("”", '"')
                return loc
            return None
        except Exception as e:
            logger.warning(f"Ollama error: {e} (will use fuzzy fallback)")
            return None

    def _fuzzy_heal(self, intent: str, candidates: list[dict]) -> Optional[str]:
        stop = {"the","a","an","button","field","element","click","on","in","that","for","to","of","and","or","is","main","primary"}
        intent_words = [w.lower() for w in re.findall(r'\w+', intent) if w.lower() not in stop and len(w) > 1]
        if not intent_words: return None
        best_score = 0.0
        best_loc = None
        for c in candidates:
            searchable = " ".join([c.get("text",""),c.get("id",""),c.get("data_testid",""),c.get("name",""),c.get("placeholder",""),c.get("aria_label","")]).lower()
            cand_words = set(re.findall(r'\w+', searchable))
            if not cand_words: continue
            score = 0.0
            for iw in intent_words:
                if iw in searchable: score += 1.0
                else:
                    if difflib.get_close_matches(iw, list(cand_words), n=1, cutoff=0.6): score += 0.6
            norm = score / max(len(intent_words), 1)
            if norm > best_score and norm >= 0.25:
                best_score = norm
                best_loc = self._candidate_to_locator(c)
        return best_loc

    def _candidate_to_locator(self, c: dict) -> str:
        if c.get("data_testid"): return f'locator("[data-testid=\\"{c["data_testid"]}\\"]")'
        eff_name = c.get("aria_label") or c.get("text") or c.get("name")
        eff_role = c.get("role") or ("button" if c.get("tag") == "button" else "")
        if eff_role and eff_name:
            esc = eff_name.replace('"', '\\"')
            return f'get_by_role("{eff_role}", name="{esc}")'
        if c.get("id"): return f'locator("#{c["id"]}")'
        if c.get("text"): return f'get_by_text("{c["text"].replace(chr(34), chr(92)+chr(34))}", exact=False)'
        return f"locator('{c.get('tag')}')"

    def _safe_eval(self, page, locator_str: str):
        allowed = ("get_by_role","get_by_text","get_by_label","get_by_placeholder","get_by_test_id","locator")
        expr = locator_str.strip()
        if expr.startswith("page."): expr = expr[5:]
        if not any(expr.startswith(a) for a in allowed):
            expr = f'locator("{expr}")'
        return eval(f"page.{expr}", {"__builtins__": {}}, {"page": page})

    def stats(self) -> str:
        return f"Healed {self.heal_count} locator(s), cache size: {len(self.cache)}"
