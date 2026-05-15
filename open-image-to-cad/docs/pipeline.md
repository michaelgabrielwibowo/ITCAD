# Pipeline
1. Image/Text -> LLM Adapter
2. Returns -> CADBrief JSON
3. LLM Adapter (Brief -> Code)
4. Runner executes code in sandbox
5. Runner extracts STEP/STL and computes ValidationReport
6. If error -> feeds back to LLM Adapter for Repair (up to 3 times)
