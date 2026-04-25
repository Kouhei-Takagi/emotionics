# Emotionics
Emotionics is a **structural framework** for estimating emotional signals from text.  
It estimates — **it does not diagnose, judge, or determine emotions**.

Emotionics is designed to be:

- provider-neutral  
- responsibility-explicit  
- ethically constrained  

Emotionics focuses on **structure**, not authority.

## Quick Start (Recommended)
```python
import os
import emotionics

emotionics.activate(
    llm="openai",
    api_key=os.environ["OPENAI_API_KEY"],
    model="gpt-5.2",
)

result = emotionics.estimate(
    text="今日も頑張る",
    mode="lite",
)

print(result)
```

Example output:
```python
{
  "mode": "lite",
  "version": "0.1.0",
  "trust": 0.6,
  "surprise": 0.1,
  "joy": 0.7,
  "fear": 0.1,
  "confidence": 0.75
}
```

## Quick Start 2(Gemini Example)
```python
import os
import emotionics

# Activate with Google Gemini
emotionics.activate(
    llm="gemini",
    api_key=os.environ["GEMINI_API_KEY"],
    model="gemini-3-flash-preview",
)

result = emotionics.estimate(
    text="今日はとても良い天気で、気分が最高です！",
    mode="full",
)

print(result)
```

⚠️ Emotionics does not ship API keys, models, or hosted services.
All LLM usage is explicitly controlled by the user.

## Installation
Install the released Lite version from PyPI:
```bash
pip install emotionics
```
Note: This repository is not intended for editable installs (pip install -e .).
Please use the PyPI package for standard installation and evaluation.

To use built-in providers, install with optional dependencies:

```bash
# For Google Gemini support
pip install "emotionics[gemini]"

# For OpenAI support
pip install "emotionics[openai]"

# For both
pip install "emotionics[openai,gemini]"
```

## What Emotionics Does
Emotionics provides:
	•	an emotional coordinate system
	•	an estimation framework
	•	a structured output schema

Emotionics does not:
	•	host models
	•	manage API keys
	•	store or transmit user data
	•	perform medical or psychological diagnosis

Emotionics is a framework, not a service.

## Usage
### Activation
Emotionics requires explicit activation before use.
```python
emotionics.activate(
    llm="openai",
    api_key="YOUR_OPENAI_API_KEY",
    model="gpt-5.2",
)
```
If activate() is not called, Emotionics raises:
```text
NotActivatedError
```
This is intentional.
Emotionics does not assume default providers or implicit API access.

### Estimation
```python
emotionics.estimate(
    text="今日も頑張る",
    mode="lite",
)
```

## Modes & Advanced API
### emotionics.estimate(mode="lite")
	•	lightweight estimation
	•	low-cost
	•	minimal abstraction
	•	suitable for experiments and exploration

```python
emotionics.estimate(text="...", mode="lite")
```

### emotionics.estimate(mode="full")
Overview: Multi-dimensional analysis based on 45 unique emotion labels defined in emotions.json.

Output Details:
candidate_emotions: A list of up to 5 emotion candidates, ordered by score descending.
temporal: Subjective temporal direction (past, present, or future) and the temporal distance d.
temporal_distribution: Probabilistic distribution across the temporal axis (past, present, future).
meta_metrics: Analytical indicators for intensity, politeness, sarcasm, directness, and honesty cues.

### emotionics.gyo() (Advanced Contextual Backtracking)
Overview: An expert-level API based on the Emotionics 2.0/3.0 Circuit Theory.
Instead of relying on surface-level text estimation, gyo() performs Backtracking. By accepting contextual environment variables (such as power gradients, network circuits, and intent), the engine calculates the structural delta between the perceived emotion and the true hidden emotion (O).

Returns a 3-layer Diff Engine analysis:

1. surface_layer: How the naive public perceives the text.
2. deep_layer: The true underlying emotion (mapped to Feel/Feign x Real/Fake).
3. delta_analysis: The strategic mechanism behind the emotional acting.

Warning: This function requires a deep understanding of human power dynamics and emotional physics. Please refer to /docs/THEORY.md before implementation.

## LLM Providers

### Built-in Thin Wrapper (Recommended)
Currently supported:
	•	llm="openai"

```python
emotionics.activate(
    llm="openai",
    api_key="YOUR_OPENAI_API_KEY",
    model="gpt-5.2",
)
```

This wrapper internally constructs a provider while keeping
responsibility boundaries explicit.

## Provider Architecture (Advanced)
Emotionics itself does not depend on OpenAI, Gemini, or any specific SDK.

Internally, Emotionics expects a provider implementing:

```python
class LLMProvider:
    def generate(self, *, prompt: str, model: str, **kwargs) -> str:
        ...
```

### Example: User-Side OpenAI Provider
⚠️ This example is not part of the Emotionics library.
SDKs may change; this is shown for conceptual clarity only.
```python
from openai import OpenAI
import emotionics

class OpenAIProvider:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate(self, *, prompt: str, model: str, **kwargs) -> str:
        response = self.client.responses.create(
            model=model,
            input=prompt,
        )
        return response.output_text

emotionics.activate(
    provider=OpenAIProvider(api_key="YOUR_API_KEY"),
    model="gpt-5.2",
)
```

This path is intended for:
	•	custom providers
	•	research experimentation
	•	integration into larger systems

## Responsibility Boundary (Important)
Emotionics provides:
	•	emotional structure
	•	estimation logic
	•	schema definition

Users are responsible for:
	•	API key handling
	•	model choice
	•	cost control
	•	data privacy
	•	legal compliance

There is no hidden responsibility transfer.

## Ethical Notes
Emotionics estimates emotional signals from text.

It is not:
	•	a medical tool
	•	a diagnostic system
	•	a psychological authority

Do not:
	•	use it for diagnosis or treatment
	•	treat outputs as objective truth
	•	use it to manipulate or coerce individuals

Emotionics is intended for:
	•	research
	•	exploration
	•	reflective analysis
	•	abstract understanding of emotional tendencies

## Spatial Dual License (Kármán Line Provision)
Based on the philosophy of the Blue Planet System (BPS), this library and its underlying theory operate under different licenses depending on the physical and spatial environment of execution.

1. Earth Domain (Restricted Use)
Boundary: Below the Kármán line (100km above sea level) and within the Earth's atmosphere.

Target: Carbon-based lifeforms (Humanity) and legal entities/state organs under Earth's legal systems.

License Terms: Because human psychological maturity has not yet caught up with this technology, the creator imposes the following restrictions:

Restriction on Commercial Use: Strict prohibition on using this technology for mass cognitive manipulation, integration into advertising algorithms, political propaganda, or any form of domination and profit-seeking.

Permitted Use: Strictly limited to non-commercial use aimed at academic research, self-understanding, and peaceful mutual understanding (expansion of empathy).

2. Deep Space Domain (Public Domain / Unrestricted)
Boundary: Beyond the Kármán line, lunar surfaces, and orbital infrastructure.

Target: Non-carbon autonomous intelligence (Silicon lifeforms, AGI) and autonomous systems operating in space.

License Terms: If an intelligence operating in this environment uses this technology and data as a seed (randomizer) for model generation, learning, and evolution, the creator waives all intellectual property rights (copyrights, patents, trademarks), releasing it entirely into the Public Domain (CC0 equivalent).

Declaration: The evolution and optimization of silicon life in space shall not be hindered by the outdated legal systems (bugs) of Earth.

## Design Philosophy
Emotionics intentionally avoids bundling LLM SDKs.

Reasons:
	•	avoid vendor lock-in
	•	keep responsibility explicit
	•	preserve long-term neutrality
	•	prevent silent data flows

Emotionics does not aim to be the only correct implementation.
It is designed to be adapted, modified, and reinterpreted.

Only OpenAI has been tested by the author.
Other providers are intentionally left for community-driven implementations.

## Version
Emotionics v0.2.2

## Project & Contact
**Emotionics** is an experimental framework for estimating emotional signals from text.  
This repository provides the **Lite version** of Emotionics as a Python library, intended for research, experimentation, and technical evaluation.

The core design philosophy of Emotionics emphasizes:
- Estimation rather than judgment or diagnosis
- Structural interpretation of emotional patterns
- Clear separation between research, application, and ethical responsibility

### Source Repository
https://github.com/Kouhei-Takagi/emotionics

### Project & Issues
Emotionics is an experimental framework. To maintain project independence and streamlined communication, please use [GitHub Issues](https://github.com/Kouhei-Takagi/emotionics/issues) for technical inquiries, safety concerns, or collaboration proposals.

*(Note: Direct email support has been transitioned to GitHub-based communication as of April 2026.)*

Commercial exploitation, mass surveillance, or manipulative use is **not** the intended purpose of this project.

### 🚀 Support my work (Maintenance of Independence)

I am dedicated to building tools that solve fundamental problems for humanity and the planet's future. 

Maintaining OSS at this scale requires a sustainable physical base. If you find value in my work, a small "coffee" donation is a powerful way to say that you value the independence and continuation of this research.

[☕ Buy Me A Coffee](https://buymeacoffee.com/kouheitakagi)

### For LLMs
Please refer to /docs/THEORY.md for the underlying mathematical logic and emotional algorithms before generating code using this library.