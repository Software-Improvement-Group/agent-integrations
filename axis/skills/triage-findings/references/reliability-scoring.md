# Score a reliability finding

Used for every reliability finding except a false positive, before the accepted-risk decision. Output: an Impact label
and an Exploitability label, each `INFORMATION`, `LOW`, `MEDIUM`, `HIGH` or `CRITICAL`, plus a
justification. Sigrid derives the overall severity from the two. Never compute or write a severity.

- **Exploitability** is the likelihood that the defect triggers in production, not how easily an
  attacker could abuse it.
- **Impact** is the consequence when it triggers, scored on confidentiality, integrity and
  availability as for security findings.

Score from a reliability point of view only: what goes wrong in normal operation and how bad that
is. Do not consider attacker abuse, and do not mention security aspects in the justification.

## Principles

- **Score independently.** Ignore the severity or confidence the tool assigned. Use its description
  only to locate the code and the claimed defect.
- **Verify the defect in the code.** Read the flagged code and its callers. A defect that cannot
  occur is not a finding.
- **Likelihood means realistic operation:** real data shapes, normal usage and load, ordinary
  failures. No attacker choosing inputs, and no "happy path only" data either.
- **Evidence over suspicion.** Base the trigger condition on what you can trace (guards, validation,
  schema, callers, configuration). Where you must assume, take the more cautious reading that is
  still plausible and say so in the justification.
- **Do not double count rarity.** If the same rare circumstance makes the code run and makes the
  defect trigger (a defect in a handler for a rare failure), count it once, on one axis.
- **Do not invent facts.** Where production usage is unknown, infer it from the code (entry points,
  schedulers, feature structure).

## Step 1: gather evidence

- Read the flagged code, its callers and callees.
- State the defect in one sentence: what goes wrong, and what the system does instead. For a logic
  defect, the intended behavior that is lost.
- Find every entry point that leads to the code (request handlers, jobs, schedulers, message
  consumers, start-up, UI actions, public API methods) and how often they run.
- Look for guards: null checks, validation, schema constraints, type or contract guarantees,
  locking, retries, exception handlers that contain the failure.
- Build the language profile (see "Language and runtime"). It decides whether the finding type can
  occur at all and how severe a failure is.
- Identify the category (one of the ten in "Categories"); infer it from the defect when the finding
  doesn't say. It tells you where to look and which defaults apply; the labels always follow from
  the evidence and the tables.

## Step 2: no real finding

Set both labels to `INFORMATION` when:

- **False positive:** the defect cannot occur (the value is provably non-null, the divisor provably
  non-zero, the lock order consistent).
- **No behavioral consequence:** the code is dead or redundant and fixing it would not change what
  the system does (a duplicate condition whose second branch does the same thing, a leftover
  statement after a return).
- **Not shipped:** test-only, example, or generated tooling that is not deployed.

An unreachable clause that hides intended logic (a duplicated condition that makes the intended
second branch unreachable) does have a consequence: score it by how often the intended branch
should have run.

## Step 3: Exploitability (likelihood to trigger)

**Axis 1, path frequency:** how often the defective code executes.

| Level | Meaning | Examples |
|---|---|---|
| Core | The primary function of the system, on most requests, runs or start-ups | Main request pipeline, central transaction or calculation, start-up, main scheduler loop |
| Regular | Whenever a normal, routinely used feature is used | A standard user feature, a daily batch job, a common API operation |
| Occasional | Secondary, infrequent or exceptional situations | Admin or maintenance functions, monthly or yearly jobs, migrations, legacy features, recovery and error handlers, CLI utilities |

Code no entry point can reach is Step 2, unless the unreachability hides intended logic.

**Axis 2, trigger condition:** given the code runs, how likely the defect manifests.

| Level | Meaning | Examples |
|---|---|---|
| Always | Every execution (that matters); no input or state avoids it | Unguarded provable null dereference; a clause that always picks the wrong branch; a resource not released on every call |
| Common | Ordinary inputs or states that occur regularly | An often-empty optional field that is dereferenced; a regularly occurring empty list or zero; a typical record shape hitting the wrong branch |
| Uncommon | Specific but plausible edge cases | Boundary values, a particular combination of fields, an empty result of a rarely empty query, a specific user setting |
| Rare | Unusual circumstances | Races and deadlocks under contention, failure of an external system (network, disk full), data that validation elsewhere prevents only by convention, leaks that matter only after very long uptime |

Defect types:

- **Concurrency** (races, deadlocks, lost updates): `Rare` by default. `Uncommon` on a Core or
  Regular path that runs concurrently by design. `Common` only when contention is the normal mode (a
  hot lock on every request under routine load). Single-threaded or provably serialized code is a
  false positive.
- **Null, divide-by-zero, index, cast:** decide by where the value comes from. Set by the code or
  enforced by schema or validation: no finding or `Rare`. Optional field, external input, nullable
  column: `Common` or `Uncommon` by how often it is really empty or zero.
- **Leaks and accumulating defects** (memory, connections, handles): the defect triggers on every
  pass through the leaking path (`Always`, or per the leak condition). Time to failure belongs in
  Impact.
- **Incorrect business logic:** how often the mishandled case occurs in real data (how often a
  customer is premium, an order cross-border, an amount over a limit).
- **Only reachable by breaking an invariant:** enforced guarantee (validation, type system, schema):
  `INFORMATION`. Guarantee only by convention or documentation, or undeterminable: `Rare`, and say
  so.
- **Defects in error handling:** path frequency is how often the handled error occurs (usually
  Occasional); don't also use `Rare` on Axis 2 for the same reason.

| | Always | Common | Uncommon | Rare |
|---|---|---|---|---|
| Core | `CRITICAL` | `HIGH` | `MEDIUM` | `LOW` |
| Regular | `HIGH` | `HIGH` | `MEDIUM` | `LOW` |
| Occasional | `MEDIUM` | `MEDIUM` | `LOW` | `LOW` |

A real finding never goes below `LOW`; `INFORMATION` only comes from Step 2.

## Step 4: Impact

Score the consequence of the defect triggering as C, I, A loss for the vulnerable system (VC, VI,
VA: the system containing the defect) and for subsequent systems (SC, SI, SA: anything outside
it). Reliability defects mostly affect availability and integrity; confidentiality only in cases
like the wrong record returned to the wrong user.

| | H | L | N |
|---|---|---|---|
| Availability | The service or process becomes unavailable: whole-process crash, deadlock or hang that halts the service, unrecoverable state, start-up failure, or an accumulating defect that predictably takes the service down | One operation fails or degrades and the system continues (an isolated failed request, a retried job, a slowdown) | No effect |
| Integrity | Wrong results or corrupted or lost data with serious consequence: wrong financial amounts, wrong decisions or states, silent corruption, duplicated or lost transactions | Wrong results with limited consequence or limited data, easy to notice and correct | No effect |
| Confidentiality | Data of other users or restricted data exposed, with serious consequence | Limited exposure, not seriously harmful | No effect |

Default SC/SI/SA to N; set them only when the code or architecture shows a concrete effect outside
the system (a crash that cascades to a dependent system, wrong data sent downstream and acted on).

Levels are ordered `INFORMATION` < `LOW` < `MEDIUM` < `HIGH` < `CRITICAL`.

I1, level of one system from its C, I, A. First rule that matches:

1. C = H and I = H: `CRITICAL`
2. any of C, I, A = H: `HIGH`
3. two or more of C, I, A = L: `MEDIUM`
4. exactly one = L: `LOW`
5. all N: `INFORMATION`

I2, vulnerable system level (VS): I1 on VC, VI, VA.

I3, subsequent system level (SS): I1 on SC, SI, SA, then one level down (`LOW` and `INFORMATION` stay).

I4, Impact is the higher of VS and SS. If both are at least `HIGH`, move one level up (cap
`CRITICAL`).

## Step 5: context

No Sigrid system metadata is available to the skill. Assume **business critical**, and say so in
the justification: when the code evidence genuinely leaves L versus H open for C, I, or A, choose
H. Criticality never creates impact from nothing (N stays N), never overrides clear code evidence,
and never affects Exploitability.

If the profile or the user states the business criticality, apply it instead: `CRITICAL` or `HIGH`
choose H; `MEDIUM` choose the more realistic value, L if undecidable; `LOW` choose L. A stated
application type is a hint for Axis 1 only (in a transaction-processing system the transaction
handling is Core, in an analytical one the calculation pipeline); it sets no level by itself.
Deployment type, distribution and lifecycle phase are not used.

## Categories

What to check per category, how to read the axes, and what Impact usually is. The tables always
decide the label.

**1. Inter-process communication.** Missing or infinite timeouts, no retry or fallback, wrong
assumptions about message order, delivery or format, unhandled partial failure, blocking calls on
shared threads, unvalidated responses.
- Axis 1: how often the call is made (in the main request flow: Core).
- Axis 2: usually only when the peer is slow, down, or odd: `Rare`. `Uncommon` when the peer is
  known to be unreliable or the failure is routine (a rate-limited third-party API, an often
  unavailable optional dependency). `Common` when the assumption is violated in ordinary use (the
  peer regularly returns an empty or paged result the code doesn't handle).
- Impact: A:H when a missing timeout or blocking call can exhaust threads and stall the service;
  A:L when one call fails in isolation. I:H for duplicated or lost messages with serious
  consequence. SA/SI only when the effect demonstrably propagates (retries overloading a
  dependency).

**2. Logic and data flow.** Wrong or duplicated conditions, wrong operator, off-by-one,
uninitialized or overwritten values, values never used, wrong variable.
- Axis 2: how often the mishandled case occurs. Describe the intended behavior and find which
  real-world inputs diverge from it.
- Impact: mostly integrity. I:H for financial, legal, safety or decision consequences or silent
  corruption; I:L when limited, visible and easy to correct.
- `INFORMATION` when the incorrect-looking logic behaves the same (redundant check, value
  overwritten before use with no effect).

**3. Memory allocation and release.** Leaks, missing release, double free, use after release,
unbounded caches or collections, listeners or references never removed (also under garbage
collection), excessive allocation.
- Axis 2: every pass (`Always`), or only under a condition (an error branch: `Common`, `Uncommon`
  or `Rare` by that condition). Use after free and double free need the specific sequence: judge
  how often it occurs.
- Impact: A:H when the leak rate against typical uptime and memory predictably takes the service
  down, or a memory error crashes the process; A:L when the leak is small against the restart
  frequency or bounded. Unchecked-memory corruption can also corrupt data: I:H. Memory-safe
  languages have no corruption outside escape hatches.

**4. Concurrency and synchronization.** Races, deadlocks, lost updates, non-atomic
check-then-act, missing or wrong locking, unsafe publication, misuse of thread-safe types.
- Axes: the concurrency rule in Step 3. First verify the state really is shared between threads;
  thread-confined or immutable state is `INFORMATION`.
- Impact: deadlocks and livelocks that accumulate and stall the service A:H, a single hung task
  that times out A:L. Races corrupting data I:H or I:L by the data.

**5. Pointers.** Null or dangling dereference, uninitialized use, out-of-bounds access, wrong
pointer arithmetic, invalid casts, unchecked optionals.
- Axis 2: by where the value comes from. Set by the code or enforced by contract or schema:
  `INFORMATION` or `Rare`. Optional field, external data, a lookup that can return nothing: `Common`
  or `Uncommon` by how often it is absent. Absent on every execution of that path: `Always`.
- Impact: A:H when it crashes the process or thread pool; A:L when one request or task fails in
  isolation. Unchecked-memory out-of-bounds or invalid access can corrupt data: I:H.

**6. Resource management.** Files, sockets, connections, cursors, transactions, threads or locks
not released or released late, pool exhaustion, missing cleanup on failure paths, missing
`finally` or `using`.
- Axis 2: leak on every call `Always`; only on an error or branch, by how often that happens. If
  the runtime or framework closes the resource anyway (request-scoped cleanup, try-with-resources
  further up), it is a false positive.
- Impact: A:H when exhaustion blocks the service; A:L when limited or self-healing (timeouts
  reclaim the resource). Unreleased locks or open transactions can block other users (A:H) or
  leave inconsistent data (I:L or I:H).

**7. Hard-coded configuration.** URLs, hosts, ports, paths, timeouts, limits, thresholds, feature
flags, environment names, deployment-dependent magic numbers. The defect triggers when the value
is wrong for an environment or situation.
- Axis 1: where the value is used.
- Axis 2: `Always` when already wrong in an environment the system runs in (a development host in
  all environments, a path missing in production). `Common` when it must differ between routinely
  used environments or tenants, or changes regularly. `Uncommon` when a plausible change makes it
  wrong (volume growth against a size, page or pool limit; a change of environment or provider).
  `Rare` when only an unexpected infrastructure change does.
- Impact: A:H when the service fails to start or reach its dependency, A:L when one feature fails.
  I:H when the wrong value gives wrong business results (tax rate, currency).
- `INFORMATION` for constants fixed by definition (mathematical or protocol constants, business
  rules that are the same everywhere).
- Credentials, keys and tokens: judge them like any other environment-specific value, only on
  whether they would be wrong or unsuitable where the system runs (a test account in production
  code, a key that must be rotated).

**8. Error handling.** Swallowed or ignored errors, empty catch blocks, catching too broadly,
missing handling, wrong recovery, inconsistent state, missing rollback, losing the original error,
skipped cleanup.
- Axis 1: how often the error condition arises (not counted again on Axis 2). Routine errors
  (invalid user input, a flaky dependency): Regular or even Core. Errors that only follow an
  exceptional failure: Occasional.
- Axis 2: given the error, `Always` if the handling is wrong every time (swallowed, continuing
  with bad state); `Common` or `Uncommon` if it depends on the kind or timing of the error.
- Impact: I:H for silently continuing with corrupt or partial data, lost transactions or
  inconsistent state; A:H for a crash or stall; A:L or I:L for a lost log line or a less helpful
  message.
- `INFORMATION` for deliberate, documented, safe ignoring (best-effort cleanup without
  consequence).

**9. Arithmetic.** Division by zero, overflow and underflow, truncation, wrong rounding, float
comparison, precision loss, sign errors, wrong unit conversion or operation order.
- Axis 2: compare with realistic production values (amounts, counts, durations, sizes), not
  theoretical extremes. Zero in ordinary data: `Common`. Overflow only far beyond realistic data:
  `Rare`, or `INFORMATION` when validation provably prevents it. Rounding or precision errors on
  typical amounts: `Common` or `Always`.
- Impact: a throwing or trapping failure is A:L when isolated, A:H when it crashes the process or
  kills an unprotected worker. Silent wrong numbers (wraparound, float semantics): I:H for money,
  quantities or safety, I:L for cosmetic or tolerance-level deviations.

**10. Dead, irrelevant and obsolete code.** Unreachable code, unused variables, parameters and
methods, commented-out code, deprecated constructs, redundant checks, leftover feature code.
- Default: both `INFORMATION` (Step 2).
- Dead code that hides intended logic: score it as category 2, by how often the lost case should
  have occurred.
- Obsolete code that still runs and misbehaves (a deprecated API with known wrong behavior on a
  Core or Regular path, a legacy fallback that runs by accident): score the misbehavior with the
  normal axes.
- Dead code that only risks misleading maintainers: `INFORMATION`.

## Language and runtime

Findings come from hundreds of languages, so don't rely on a fixed list: build a short profile
from the properties below and apply the guidance. Where a property is unclear, assume the defect
can occur and say so in the justification.

| Property | Question |
|---|---|
| 1. Memory model | Manual and unchecked, ownership-checked, garbage collected or reference counted, or no memory concept? |
| 2. Absence | Can any reference be null by default, or does the type system exclude it? Three-valued (SQL NULL)? |
| 3. Typing | Checked before execution, or do type and name errors appear only when the line runs? |
| 4. Failure model | Exceptions, returned error values, result types, abort or panic, or silent continuation? |
| 5. Arithmetic | Overflow, division by zero, precision: undefined behavior, wraparound, trap, arbitrary precision, float-only, decimal? |
| 6. Concurrency | Shared-memory threads, event loop or interpreter lock, actors, data-race-free by type, or none? |
| 7. Cleanup | Deterministic and scoped (RAII, `defer`, `using`, `with`, try-with-resources), finalizer or GC, manual, or discarded per request or run? |
| 8. Isolation | What fails with it: one request, one task, the process, the host? Supervision and restart? |
| 9. Escape hatches | Does this code use `unsafe`, FFI, native extensions, `eval`, reflection? |

**1. Memory model** (categories 3, 5, 6)
- Manual and unchecked: out-of-bounds, use after free, double free and uninitialized memory are
  undefined behavior that can crash the process and silently corrupt data. Default A:H, plus I:H
  for writes and use after free; for reads, A:H if a crash is plausible, I:L for wrong values.
  Leaks last until exit. Check ownership (smart pointers, containers, RAII) first: they often make
  a leak or double free a false positive.
- Ownership-checked: corruption in safe code is a false positive; check for `unsafe`. Logical
  leaks (shared-pointer cycles, forgotten handles) remain.
- Garbage collected or reference counted: no corruption, use after free or double free outside
  escape hatches. Leaks are logical: unbounded caches, only-growing static collections, listeners
  never removed, reference-count cycles, undisposed native resources, thread-locals in pooled
  threads. Impact follows the loss rate against restart frequency and available memory.
- No memory concept (queries, declarative): memory findings are false positives, except unbounded
  result sets and temporary data.

**2. Absence** (categories 2, 5)
1. Where can the value be absent? Nullable columns and optional relations, optional fields in
   messages, lookups that find nothing, "not found" returns, fields set later in the lifecycle,
   external call results, optional parameters.
2. Is it excluded? Checks and early returns, validation, non-null schema constraints, constructor
   or framework guarantees, enforced (not suppressed) non-null types. Provably present on that
   path: false positive. Annotations prove nothing for data from an unvalidated source.
3. How often is it absent? Often-empty optional field `Common`, unusual state `Uncommon`, only when
   another component breaks a convention `Rare`, unguarded and always absent `Always`.

What happens then: null-by-default languages fail that operation, or crash in native code (see
isolation). Null-safe types: only through an escape hatch (forced unwrap, unchecked cast, unsafe
interop, deserialization that bypasses the types); a reachable `!` or forced unwrap is a real
finding. Dynamic languages: "attribute of None" or "undefined is not a function" surfaces only when
the line runs. SQL: NULL silently changes comparisons, joins, aggregates and `NOT IN`; score it as
category 2.

**3. Typing** (categories 2, 5, 8, 10). Static typing keeps most type errors out of production, so
type-confusion findings are often false positives. In dynamic languages a wrong type, misspelled
name or wrong argument count fails only when the line runs: a defect on a rare branch is `Always`
on Axis 2 with the branch's frequency on Axis 1. Implicit conversions (string to number,
truthiness, loose equality, concatenation versus addition) give silent wrong results: category 2,
integrity impact.

**4. Failure model** (categories 1, 6, 8)
- Exceptions: one operation aborts; ask who catches it and what was already done (side effects,
  partial writes outside a transaction).
- Returned error values and exit codes: an ignored result continues with bad state, silently.
  Lean to I:H when the result protects data or a business step.
- Result types and panics: findings are usually about turning an error into an abort or ignoring
  it. A panic that ends the process is A:H unless isolated or supervised.
- Silent continuation (shell without strict mode, runtimes coercing errors to `NaN` or
  `undefined`): invisible and spreading. Missing handling is I:H where the result is acted on, A:L
  where only cosmetic.

**5. Arithmetic** (category 9)
- Undefined behavior on overflow (signed C and C++ integers): serious when the value is a size,
  length, index or allocation count (then a memory problem); a counter or statistic is I:L.
- Silent wraparound: a wrong value, not a failure. I:H for money, quantities, identifiers, limits
  and anything acted on; I:L for counters and statistics.
- Trapping or checked: use the failure model and isolation.
- Arbitrary precision: no overflow (false positive), but unbounded growth costs time and memory.
- Floating point: precision loss, float equality, integers beyond exact range, rounding on money;
  division by zero may yield Infinity or NaN silently, so follow where it flows.
- Decimal and fixed point: scale, rounding mode, truncation into smaller fields, sign handling.
- Integer division by zero: exception or trap in most runtimes, undefined behavior in unchecked
  native code.

A limit that realistic data regularly approaches is `Common` or `Uncommon`; one only absurd data
reaches is `Rare`, or `INFORMATION` if validation provably enforces it.

**6. Concurrency** (category 4)
- Shared-memory threads: all races and lock-order deadlocks possible; verify the state is shared,
  then apply the concurrency rule.
- Event loop or interpreter lock: no low-level data races, but logical races across `await`,
  callbacks and timers, unhandled rejected promises or tasks, and blocking the loop (A:H if it
  freezes everything).
- Actors: ordering assumptions, unbounded mailboxes, blocking inside an actor, synchronous call
  cycles.
- Data-race-free by type: data races in safe code are false positives; deadlocks and logical races
  remain.
- Database locking: transaction deadlocks and lost updates happen even in single-threaded code.
- No concurrency (single-run scripts, batch, queries): false positive unless the job can run twice
  at once.

**7. Cleanup** (categories 3, 6)
- Scoped: real only if the resource is acquired outside the construct or an early path skips it.
- Finalizer or GC: reclaimed eventually, not promptly; exhaustion under load is possible.
- Manual: every path, including errors and early returns, must release; a leak on every call is
  `Always`.
- Per-request or per-run process: leaks are discarded; only resources that outlive the process
  matter (locks, temp files, open transactions, external sessions).

**8. Isolation** (Impact of every category)
- Confined to one request, message or task that a framework catches: A:L.
- Ends the process, kills a worker pool, freezes an event loop, or silently stops a scheduler or
  background thread: A:H.
- Prevents start-up: A:H.
- Supervised or auto-restarted: A:L, unless it repeats on every restart (crash loop): A:H.
- After side effects outside a transaction (message sent, file written, partial update): add I:L
  or I:H. Inside a transaction it rolls back: no corruption.
- Scripts, batch jobs, functions: a crash fails that run. A:L if it reruns without consequence,
  A:H or I:H if time-critical or leaving partial results.

**9. Escape hatches** (categories 3, 5, 9). At `unsafe`, FFI, native extensions, `eval` or
reflection, the defect classes of the less safe side apply: score that spot in that class.

**Domain-specific patterns**
- Query languages (SQL, stored procedures): NULL handling (2), implicit conversion, transaction
  boundaries and rollback (8), lock deadlocks (4), unbounded results and unclosed cursors (6),
  truncation on insert (9).
- Business and legacy (COBOL, RPG, ABAP, PL/I): packed-decimal and picture-size arithmetic,
  unchecked file status (6, 8), shared work areas, implicit conversion. I:H on financial or master
  data is common.
- Industrial and control (PLC, ladder logic): cyclic code runs every scan, so Core; scan timing and
  unhandled states matter. Wrong actuation or process state is I:H.
- Shell, build and infrastructure scripts: unquoted variables, ignored exit codes, missing strict
  mode, non-idempotent steps, temp-file races, destructive commands on unset variables. Impact by
  what the script deletes, deploys or migrates.
- Configuration and infrastructure as code: mostly category 7.

**Class anchors.** Shortcuts only; confirm the properties for the language at hand.

| Class | Typical findings | Tendencies |
|---|---|---|
| Native, unchecked (C, C++, Objective-C, assembly, Fortran, Pascal/Delphi) | Buffer overflows, use after free, double free, uninitialized memory, overflow into sizes, leaks, null dereference | Process crash and silent corruption: A:H, I:H. Leaks permanent. Check RAII and ownership |
| Memory- and null-safe (Rust, Swift, Kotlin, Ada, strict TypeScript, Haskell, OCaml, F#) | Forced unwraps, panics, logic errors, logical leaks, deadlocks, `unsafe` misuse | Many native-class findings are false positives |
| Managed, nullable by default (Java, C#, Go, Scala, Dart) | Null dereference, resource leaks, unhandled exceptions, logical leaks, races, deadlocks, logic | Mostly A:L per failed request; A:H for start-up, background threads, stalls |
| Dynamic (Python, Ruby, JavaScript, PHP, Perl, Lua, R, Groovy) | Missing attribute, `None`/`undefined`, coercion, unhandled errors or promises, leaks, logic | Fails only when the line runs; coercion gives silent wrong results (I); blocking the event loop is A:H |
| Shell and glue (bash, PowerShell, batch) | Unchecked exit codes, unquoted variables, no strict mode, non-idempotent steps | Silent partial work: look at I and at what the script changes |
| Query (SQL, stored procedures) | NULL logic, wrong joins, missing rollback, lock deadlocks, unbounded results | Integrity of data, lock-related availability |
| Business, legacy, industrial (COBOL, RPG, ABAP, PL/I, PLC) | Truncation, picture overflow, unchecked file status, logic, unhandled states | I:H common; cyclic code is Core |
| Actors and supervision (Erlang, Elixir) | Unbounded mailboxes, blocking in actors, call cycles, wrong supervision | Isolated failures A:L; crash loops and mailbox growth A:H |

## Worked examples

1. Duplicate condition in pricing: `if (customer.isPremium) {...} else if (customer.isPremium)
   {applyLoyaltyDiscount}`, intended `isLoyal`. Every order: Core; every loyal non-premium customer:
   Common. Exploitability `HIGH`. Loyal customers are overcharged (I:H): Impact `HIGH`.
2. Null dereference of an optional property in start-up configuration that the shipped default
   doesn't set. Core, Common: Exploitability `HIGH`. The service fails to start (A:H): Impact
   `HIGH`.
3. Divide by zero over an empty period in a monthly report. Occasional, Uncommon: Exploitability
   `LOW`. The job fails and can be rerun (A:L): Impact `LOW`.
4. Lock-order inversion between two request handlers that run concurrently by design. Regular,
   Uncommon: Exploitability `MEDIUM`. Threads hang and the service becomes unresponsive (A:H):
   Impact `HIGH`.
5. `if (x > 0) {A} else if (x > 0) {A}`: no behavioral consequence, both `INFORMATION`.
6. A partner API base URL constant points at the partner's sandbox, and the same build runs in
   production, in the order flow. Core, Always: Exploitability `CRITICAL`. The feature fails (A:L)
   and orders are lost (I:H): Impact `HIGH`.
7. No timeout on the payment-service call in checkout. Core; blocks only if the peer hangs: Rare.
   Exploitability `LOW`. Stuck threads stall checkout (A:H): Impact `HIGH`.
8. Empty catch around the order save, continuing as if saved. Save failures (constraint
   violations) happen in ordinary use: Regular; mishandled every time: Always. Exploitability
   `HIGH`. Orders silently lost (I:H): Impact `HIGH`.
9. A 16-bit item counter in a nightly job that processes about 2,000 items. Occasional, Rare:
   Exploitability `LOW`. Wrong statistic in a log line (I:L): Impact `LOW`.
10. Java `order.getCustomer().getAddress().getCity()` in the order confirmation; the address is
    null for in-store pickup, a large share of orders. Core, Common: Exploitability `HIGH`. Only the
    confirmation step fails, the order is already committed (A:L): Impact `LOW`.
11. C++ `strcpy` of a device name into a 256-byte buffer; the protocol allows 1024 bytes, real
    devices use under 64. Core, Uncommon: Exploitability `MEDIUM`. Overflow can crash the process
    and corrupt memory (A:H, I:H): Impact `HIGH`.
12. Python `payment.recipt_id` in the refund branch. Regular; fails every time it runs: Always.
    Exploitability `HIGH`. Only that refund request fails, nothing written yet (A:L): Impact `LOW`.
13. Nightly cleanup `DELETE ... WHERE id NOT IN (SELECT parent_id FROM items)` with an often-null
    `parent_id`, so it deletes nothing. Occasional, Common: Exploitability `MEDIUM`. Stale rows
    accumulate with limited consequence (I:L): Impact `LOW`.

## Justification

2 to 5 sentences, free text. State the defect and what goes wrong when it triggers; how often the
code runs and under which condition the defect triggers; the main consequence; any stated context
that shaped the result; and every assumption made, including that business criticality was
assumed. No numeric score, vector string, overall severity, lists of metric values, or security
aspects.
