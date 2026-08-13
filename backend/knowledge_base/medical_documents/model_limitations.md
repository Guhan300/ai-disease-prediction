# Model Estimates vs Medical Diagnosis

MedAI uses a trained machine-learning classifier to rank possible conditions from
structured symptom features extracted during conversation.

## What the model does

- Converts symptom presence into features
- Outputs class scores for educational ranking
- Can be explained with feature-contribution methods such as SHAP

## What the model does not do

- Confirm a medical diagnosis
- Replace clinical examination or laboratory tests
- Prescribe medication
- Provide emergency triage guarantees

## Safety notes

If symptoms suggest an emergency (severe breathing difficulty, severe chest pain,
loss of consciousness, severe allergic reaction), seek appropriate emergency care
immediately.
