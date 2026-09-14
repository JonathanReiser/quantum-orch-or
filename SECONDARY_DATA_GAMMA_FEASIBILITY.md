# Can public data test the somatic gamma map?

**Decision: no-go for the proposed calibration analysis with currently
identified public data.** This screen was performed before downloading or
analyzing participant signals. It prevents a nearby but different dataset from
being presented as a test of cognitive recovery.

## What the data must contain

To test the proposed wearable-to-gamma link, one dataset must contain:

1. beat-level ECG or another defensible reference signal;
2. wearable beat timing or a signal from which comparable HRV can be derived;
3. a demanding task with recorded performance;
4. repeated cognitive performance measurements during recovery;
5. participant identifiers and timing needed to hold people out during testing;
6. enough information about breathing and movement to address major HRV
   alternatives.

The fourth requirement is essential. ECG recorded during recovery is not a
cognitive recovery outcome.

## Datasets screened

| Dataset | Useful material | Why it cannot answer the question |
| --- | --- | --- |
| [EEG–ECG stress and mental-workload dataset](https://doi.org/10.17632/s87jk3p5ws.1) | Neutral and stress sessions, arithmetic performance, 1,000 Hz ECG, and a five-minute post-task recovery period | The published description does not identify repeated cognitive-task measurements during recovery. It can measure cardiac recovery, not the proposed cognitive recovery curve. |
| [CLAS](https://snlab.site123.me/clas) | ECG, PPG, movement, math/logic/Stroop answers, and 62 participants | The protocol contains task blocks and short neutral material, but not repeated cognitive measurements across a recovery period. Full access also requires an EULA. |
| [WESAD](https://doi.org/10.1145/3242969.3242985) | ECG, respiration, movement, baseline, stress, amusement, and meditation | Designed for stress and affect recognition; it does not provide the required repeated cognitive-performance recovery outcome. |
| [Wearable Exam Stress dataset](https://doi.org/10.13026/kvkb-aj90) | Wearable inter-beat intervals and grades across three real exams | Grades are session-level outcomes. There is no controlled post-task cognitive recovery series or simultaneous research ECG reference. |
| [QoL_Stress](https://doi.org/10.5281/zenodo.20757481) | ECG, wearable heart rate, movement-related signals, self-reported stress, Stroop, and gameplay in 66 adults | Contains relaxation and stress phases, but the public description does not provide repeated cognitive performance during post-stress recovery. |

## Why the nearest substitutes are not enough

Three easier analyses are possible, but none tests the gamma claim:

- predicting stress labels from HRV;
- predicting a grade or one task score from HRV;
- fitting an exponential curve to cardiac recovery alone.

Calling any of those “gamma calibration” would change the outcome after seeing
what data are convenient. The simulator's `p_choice_1` is a cognitive-choice
probability, not heart rate, a stress label, or an exam grade.

## What would change the decision

Proceed with secondary-data calibration only if a dataset is found that includes
time-aligned reference cardiac data **and** repeated task performance throughout
recovery. The study must then define what `p_choice_1` means before inspecting
outcomes and compare the gamma map against simpler models on held-out people.

If no such dataset becomes available, the defensible options are:

1. collaborate with a lab that already runs a suitable stress-and-recovery
   protocol; or
2. design a new pilot after ethics, consent, equipment, task meaning, and sample
   size are settled.

## Current conclusion

The low-cost secondary-data test cannot presently be run as specified. This is
not evidence for or against the gamma map. It is evidence that the required
cognitive recovery outcome is missing from the datasets screened.

No participant signup or recruitment should begin on the basis of this screen.
