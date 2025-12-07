## MediCode – ICD Assistant

MediCode is a web-based interface designed to assist medical professionals during the ICD coding process. Developed as a direct extension of the icd-coding research project, this application demonstrates how automated ICD code recommendation models can be integrated into a practical, clinician-facing workflow.
The system analyzes clinical text to generate AI-driven ICD code suggestions while allowing users to verify, search, and manually finalize the diagnosis codes.

### Interface Overview

<img width="1575" height="827" alt="스크린샷 2025-10-06 오후 1 31 26" src="https://github.com/user-attachments/assets/e4d7da8c-f8da-4c93-a047-21bbe1c59b30" />

The interface uses a dual-panel layout designed to streamline the medical coding workflow.

#### Left Panel: Document & Selection

This panel focuses on input and final decisions.
It contains:

* a Document Info field (for titles or dates),
* a large Clinical Text area for raw medical narratives (e.g., admission notes, discharge summaries),
* a Selected Codes section displaying the finalized list of diagnoses, each with a removable card.

#### Right Panel: Assist & Search

This panel acts as the intelligent assistant. It includes:

* AI-generated Top-k code recommendations derived from the clinical text,
* prediction details such as ICD code, internal index, and score (e.g., score=0.91),
* a Search Bar allowing manual lookup for prefixes or keywords (e.g., “E0”, “delirium”),
* add (+) buttons to move any recommended or searched code to the Selected Codes list.

### Key Features

#### AI-Driven Recommendation

The assistant uses an ICD prediction model to automatically analyze clinical text and display the most likely codes. The number of displayed recommendations can be adjusted (e.g., top-5).

#### Human-in-the-Loop Interaction

Users can inspect each suggested code, review prediction confidence, and selectively add desirable codes to the final list. This keeps medical professionals in full control of the final output.

#### Search & Verification

The search function enables clinicians to look up additional codes that might not appear in the automated recommendations, ensuring completeness and accuracy.

### Usage

1. Enter the document title or date in the Document Info field.
2. Paste the patient’s clinical note into the Clinical Text box.
3. Review the AI-generated recommendations in the right-hand Assist panel.
4. Optionally search for additional ICD codes using keywords or prefixes.
5. Click the plus (+) icon to add a code to your final Selected Codes list.
6. Remove any incorrect codes using the trash icon in the Selected Codes area.

## Installation

Clone the repository:

```
git clone https://github.com/shchooii/MediCode.git
```

The project contains two main folders:

```
MediCode/
├── be/     Python backend (API server, prediction handler)
└── fe/     Frontend (UI implementation)
```

This repository **does not include model files or training code**.
To enable real ICD predictions, add your own model to `be/` and implement a simple prediction function.

## Running the Application

### Backend (Python)

```
cd MediCode/be
pip install -r requirements.txt    # if available
uvicorn main:app --reload
```

Backend default URL:

```
http://localhost:8000
```

### Frontend

If the frontend is static:

```
cd MediCode/fe
python -m http.server 5173
```

If it uses a JS framework:

```
cd MediCode/fe
npm install
npm run dev
```

Frontend default URL:

```
http://localhost:5173
```

Make sure the frontend API base URL matches the backend endpoint.

## Adding Your ICD Prediction Model

Place your model code or weights inside:

```
be/model/
```

Implement approximately:

```python
predict(text) -> [{"code": "...", "description": "...", "score": 0.00}]
```

Connect this function to the backend prediction route.

## Research Background

MediCode is an applied extension of the icd-coding research project,
which explores long-tailed multi-label ICD classification, imbalance-aware loss functions,
and improved prediction pipelines for ICD-10 coding.
This interface demonstrates how those research outcomes can be integrated into a real workflow to support clinical decision-making.

🔗 Research Project: https://github.com/shchooii/icd-coding
