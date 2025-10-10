import modal
from modal import App, Image

# Setup

app = modal.App("pricer")
image = Image.debian_slim().pip_install("torch", "transformers", "bitsandbytes", "accelerate", "peft")
secrets = [modal.Secret.from_name("hf-secret")]

# Constants

GPU = "T4"
BASE_MODEL = "meta-llama/Meta-Llama-3.1-8B"
PROJECT_NAME = "pricer"
HF_USER = "shreshre" 
RUN_NAME = "2025-10-08_13.04.39"
PROJECT_RUN_NAME = f"{PROJECT_NAME}-{RUN_NAME}"
REVISION = "e8d635df551603dc86cd7a1598a8f44af4d7ae23"
FINETUNED_MODEL = f"{HF_USER}/{PROJECT_RUN_NAME}"


@app.function(image=image, secrets=secrets, gpu=GPU, timeout=1800)
def price(description: str) -> float:
    import os
    import re
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, set_seed
    from peft import PeftModel

    QUESTION = "How much does this cost to the nearest dollar?"
    PREFIX = "Price is $"

    prompt = f"{QUESTION}\n{description}\n{PREFIX}"
    
    # Quant Config
    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_quant_type="nf4"
    )

    # Load model and tokenizer
    
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL, 
        quantization_config=quant_config,
        device_map="auto"
    )

    fine_tuned_model = PeftModel.from_pretrained(base_model, FINETUNED_MODEL, revision=REVISION)

    set_seed(42)
    inputs = tokenizer.encode(prompt, return_tensors="pt").to("cuda")
    attention_mask = torch.ones(inputs.shape, device="cuda")
    outputs = fine_tuned_model.generate(inputs, attention_mask=attention_mask, max_new_tokens=5, num_return_sequences=1)
    result = tokenizer.decode(outputs[0])

    contents = result.split("Price is $")[1]
    contents = contents.replace(',','')
    match = re.search(r"[-+]?\d*\.\d+|\d+", contents)
    return float(match.group()) if match else 0

"""
---

### Why `match.group()` is needed

When you do:

```python
match = re.search(pattern, contents)
```

* The variable `match` is **not** the text that matched.
* It’s a **`re.Match` object**, which contains **metadata** about the match — like:

  * the full matched text,
  * where it starts and ends in the string,
  * any groups (submatches) inside parentheses.

To actually get the **text** that was matched (e.g., `"45.67"`),
you need to call `.group()` on that match object:

```python
match.group()
```

---

### Analogy

Think of `match` as a **container** that stores info about what was matched.
`.group()` is how you **open that container** and pull out the matched text itself.

---

### Example:

```python
import re

text = "Price: 45.67 USD"
match = re.search(r"[-+]?\d*\.\d+|\d+", text)

print(match)          # <re.Match object; span=(7, 12), match='45.67'>
print(match.group())  # '45.67'
```

* `match` → is an object with data like `span=(7, 12)` (the indices in the text).
* `match.group()` → just gives you the string `"45.67"`, which you can then convert to a float.

---

So, in short:
✅ **`match`** = object describing the match.
✅ **`match.group()`** = the **actual text** that matched the regex.


"""
