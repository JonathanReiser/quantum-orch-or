# What comes next: testing the wearable-to-simulation link

**This study is still being designed. It is not yet recruiting, approved, or
preregistered.** The current model has not been shown to measure cognition,
stress, or any medical condition.

A [screen of available public datasets](SECONDARY_DATA_GAMMA_FEASIBILITY.md)
found no dataset with repeated cognitive measurements during recovery. The
secondary-data calibration is therefore a no-go unless a suitable dataset is
found or shared by a research partner.

## The idea

The project was built around a simple chain:

```text
heart-rate data from a wearable
→ change in heart-rate variability (HRV)
→ a number called gamma
→ the speed of a simulated cognitive response
```

The code that runs the simulation behaves consistently. The weak link is the
step that turns HRV into gamma. Its constants were chosen for the model; they
were not learned from people.

The [gamma-map sensitivity study](GAMMA_MAP_SENSITIVITY.md) showed why that
matters. Changing those constants changed four of the five results we tested.
The next step is therefore not another simulation. It is a real-world test of
the link itself.

## The main question

> Does a change in HRV help predict how a person's performance recovers after a
> demanding task, better than a model that ignores HRV?

The answer is allowed to be no. If HRV does not improve prediction on people
whose data were not used to build the model, the current wearable-to-gamma link
should be rejected or described much more narrowly.

## What we need from a partner

The immediate need is not more simulation work or a list of possible
participants. It is one of the following:

1. **Suitable existing data.** Beat-level reference ECG or a validated chest
   strap, a wearable measurement from the same period, a demanding task, and
   repeated measurements of cognitive performance during recovery. Movement,
   breathing, participant identifiers, and exact timing should also be
   available.
2. **Study-design and oversight support.** A researcher or institution able to
   help choose the cognitive task, validate the physiological measurements,
   review the analysis plan, provide the appropriate ethics route, and oversee
   a small repeated-measures pilot.

Possible partners include psychophysiology and cognitive-fatigue laboratories,
wearable-validation researchers, and teams already collecting ECG, movement,
breathing, and repeated task-performance data.

Data containing only stress labels, questionnaires, exam grades, or cardiac
recovery cannot answer the main question. Those are related outcomes, but they
are not measurements of cognitive recovery. The
[public-data screen](SECONDARY_DATA_GAMMA_FEASIBILITY.md) explains why the
datasets reviewed so far do not meet the full requirement.

## What the project is trying to produce

The end product is not a more elaborate equation. It is an evidence-based
decision about whether the wearable-to-gamma bridge deserves to exist.

If the idea works, the project should produce:

- a clear task-level meaning for the simulation output;
- a wearable measurement shown to agree adequately with a reference device;
- a preregistered formula learned without using the final test group;
- evidence that HRV improves prediction over a simple fixed-rate model;
- a later test on new people;
- open analysis code, versioned summary results, and a record of every change
  to the plan.

If the idea does not work, the project should produce an equally useful result:
the current bridge will be removed, rejected, or limited to a clearly labeled
toy assumption. A negative result would prevent an unvalidated constant from
being presented as physiology.

Even a positive result would have narrow meaning. It could support a predictive
link between a particular HRV measurement and recovery in a particular task.
It would not prove that cognition is quantum, validate Orch-OR, diagnose a
condition, or establish a medical product.

## First, define what the simulation means

The simulation produces a probability called `p_choice_1`. We have not yet
shown what that probability represents in a human task.

Before anyone takes part, the study must choose one simple, repeatable
two-choice task and state:

- what “choice 1” means;
- what change or recovery the model is supposed to describe;
- when each measurement will be taken;
- what result would show that the model is wrong.

Without those decisions, it would be too easy to change the meaning after seeing
the data.

## Part 1: check the wearable

The intended wearable should be compared with a research ECG or a validated
chest strap. Measurements should be taken during:

- quiet rest;
- a demanding task;
- recovery;
- ordinary movement.

We would record movement and breathing because both can change or distort HRV.
We would report disagreement, missing readings, and motion failures—not just a
correlation that might look impressive while hiding large errors.

If the wearable cannot measure HRV reliably enough in the intended setting, the
study stops there. The long-standing measurement guidance is available in the
[ESC/NASPE heart-rate variability
standards](https://www.escardio.org/static-file/Escardio/Guidelines/Scientific-Statements/guidelines-Heart-Rate-Variability-FT-1996.pdf).

## Part 2: run a small pilot

Each person would complete more than one session. A session would look roughly
like this:

```text
quiet rest
→ a controlled, demanding task
→ repeated measurements during recovery
```

We would collect:

- reference and wearable heart-beat timing;
- movement and breathing;
- task choices, accuracy, and response time;
- a short self-report of how the person feels;
- basic session details such as time of day and order.

The first pilot might involve about 30–40 adults. Its purpose would be to learn
whether the measurements are reliable, how much people differ, how strong
practice effects are, and how large a later study should be. It would not be
presented as proof that the model works.

Research has found that demanding tasks can affect both performance and
heart-rate variability, which makes the question worth testing. That research
does not establish this project's gamma formula. One relevant example is
[Nuamah, 2024](https://doi.org/10.1016/j.ijpsycho.2024.112325).

## Part 3: compare the idea with simpler explanations

We should not test only the formula we already wrote. At minimum, we should
compare:

1. one fixed gamma for everyone, which means HRV adds nothing;
2. the current formula;
3. a simple formula without the artificial upper and lower limits;
4. a model that allows normal differences between people;
5. one limited curved relationship chosen before the final test.

Every model must use the same data and rules. The HRV approach succeeds only if
it predicts the whole recovery pattern better than the fixed-gamma model.

## Part 4: test it on new people

The pilot would be used to develop the method. The final rules and code would
then be frozen before collecting a later group of participants.

That later group is essential. Testing the method on the same people used to
build it can make a weak model look better than it is. Guidance for reporting
prediction studies makes the same distinction between development and genuine
outside testing: [TRIPOD](https://doi.org/10.1136/bmj.g7594) and
[TRIPOD for repeated or grouped
data](https://www.bmj.com/content/380/bmj-2022-071058).

## What would make us reject the link?

The wearable-to-gamma idea would not be supported if:

- the wearable disagrees too much with the reference device;
- the simulation's probability cannot be tied clearly to the chosen task;
- HRV does not improve prediction over one fixed gamma;
- the apparent effect disappears after accounting for breathing or movement;
- it works in the pilot but fails on the later group;
- almost every person needs a different formula.

We would report those results rather than choosing a new formula after seeing
what happened.

## Ethics, privacy, and recruitment

This would be research involving people, physiological measurements, and a
controlled task. The study plan, recruitment language, consent process, data
handling, and any required ethics or institutional review must be settled before
enrollment or data collection. [U.S. Office for Human Research Protections
guidance](https://www.hhs.gov/ohrp/regulations-and-policy/guidance/faq/informed-consent/index.html)
explains the role of informed consent in covered research.

Recruitment and a public interest list are premature until the task has an
operational meaning, a research partner or oversight route is identified, and
the protocol and data handling have been reviewed. No health or contact data are
being collected for this proposed study at this stage.

## Open research plan

The pilot and later test would be preregistered separately. The registration
would state the questions, number of participants, exclusions, measurements,
comparison models, and analysis before results are known. The [Open Science
Framework](https://help.osf.io/article/330-welcome-to-registrations) provides
templates for doing this.

Code, changes to the plan, and negative results would be public. Identifying or
raw physiological data would not be placed in this repository.
