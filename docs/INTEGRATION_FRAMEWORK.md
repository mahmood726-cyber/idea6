# Integration Framework: Combining P-Curve, Specification Curve, and Multiverse Analysis

## Decision Tree for Integrated Robustness Assessment

This document provides formal guidelines for interpreting results when combining all three methods.

---

## Overview

The three methods answer **different questions**:

| Method | Primary Question | Evidence Type |
|--------|-----------------|---------------|
| **P-Curve** | Does the published literature contain evidential value? | Publication validity |
| **Specification Curve** | Is this finding robust to reasonable analytical choices? | Analytical robustness |
| **Multiverse Analysis** | How sensitive are results to all analytical decisions? | Sensitivity quantification |

**They should NOT be combined into a single score**, but interpreted complementarily.

---

## Decision Tree

```
START: Research Question Assessment
│
├─→ [1] LITERATURE REVIEW STAGE
│   │
│   ├─→ Do you have published p-values from multiple studies?
│   │   │
│   │   YES → RUN P-CURVE ANALYSIS
│   │   │     │
│   │   │     ├─→ Evidential Value = YES
│   │   │     │   └─→ ✓ Literature likely contains real effects
│   │   │     │       Proceed to primary analysis
│   │   │     │
│   │   │     └─→ Evidential Value = NO
│   │   │         └─→ ⚠ WARNING: Literature may be p-hacked
│   │   │             Consider:
│   │   │             - Are studies pre-registered?
│   │   │             - Publication bias likely?
│   │   │             - Worth replicating?
│   │   │
│   │   NO → Proceed to primary analysis
│   │
│   └─→ Continue to [2]
│
├─→ [2] PRIMARY ANALYSIS STAGE
│   │
│   └─→ Conduct your main pre-specified analysis
│       Report results
│       Continue to [3]
│
├─→ [3] ROBUSTNESS CHECK STAGE
│   │
│   ├─→ Are there multiple defensible analytical choices?
│   │   │
│   │   YES → RUN SPECIFICATION CURVE ANALYSIS
│   │   │     │
│   │   │     ├─→ >90% specifications significant
│   │   │     │   AND consistent sign
│   │   │     │   └─→ ✓ ROBUST: High confidence in finding
│   │   │     │
│   │   │     ├─→ 70-90% significant
│   │   │     │   AND mostly consistent sign
│   │   │     │   └─→ ✓ MODERATELY ROBUST
│   │   │     │       Identify influential choices
│   │   │     │       Report conditioned on key decisions
│   │   │     │
│   │   │     ├─→ 50-70% significant
│   │   │     │   OR sign inconsistency
│   │   │     │   └─→ ⚠ FRAGILE
│   │   │     │       Results depend heavily on choices
│   │   │     │       Report cautiously with caveats
│   │   │     │
│   │   │     └─→ <50% significant
│   │   │         └─→ ✗ NOT ROBUST
│   │   │             Effect may not be reliable
│   │   │
│   │   NO → One clear specification
│   │        Report with standard sensitivity checks
│   │
│   └─→ Continue to [4]
│
└─→ [4] COMPREHENSIVE SENSITIVITY STAGE
    │
    └─→ Do you want comprehensive sensitivity analysis?
        │
        YES → RUN MULTIVERSE ANALYSIS
        │     │
        │     ├─→ Evaluate Fragility Metrics:
        │     │   │
        │     │   ├─→ Inferential Fragility (IF)
        │     │   │   IF < 0.2  → Low fragility (robust)
        │     │   │   IF 0.2-0.5 → Moderate fragility
        │     │   │   IF > 0.5  → High fragility (fragile)
        │     │   │
        │     │   ├─→ Sign Fragility (SF)
        │     │   │   SF < 0.1  → Consistent direction
        │     │   │   SF 0.1-0.3 → Some inconsistency
        │     │   │   SF > 0.3  → Frequent sign flips
        │     │   │
        │     │   └─→ Vibration of Effects (VoE)
        │     │       VoE < 2.0  → Tight distribution
        │     │       VoE 2.0-5.0 → Moderate spread
        │     │       VoE > 5.0  → High variability
        │     │
        │     └─→ Identify most influential choices
        │         Report fragility metrics
        │         Discuss implications
        │
        NO → Standard sensitivity analysis
             Report limitations

END: Integrated Assessment Complete
```

---

## Interpretation Matrix

### Scenario 1: Strong Convergent Evidence

**Pattern:**
- P-Curve: Evidential value = YES, Power >50%
- Spec Curve: >90% significant, tight distribution
- Multiverse: IF <0.2, SF <0.1

**Interpretation:** ✓✓✓ **STRONG EVIDENCE**
- Literature shows evidential value
- Finding is robust to analytical choices
- Results are not fragile

**Recommendation:**
- High confidence in effect
- Suitable for publication and application
- Still report all analyses transparently

**Example Wording for Paper:**
> "Convergent evidence from p-curve analysis (evidential value detected, estimated power = 75%), specification curve analysis (94% of specifications significant), and multiverse analysis (inferential fragility = 0.15) indicates robust support for the hypothesized effect."

---

### Scenario 2: Mixed Evidence - Robust but Literature Questionable

**Pattern:**
- P-Curve: Evidential value = NO or p-hacking detected
- Spec Curve: >80% significant
- Multiverse: IF <0.3

**Interpretation:** ⚠✓✓ **ROBUST EFFECT, QUESTIONABLE LITERATURE**
- Published literature may be biased
- Current analysis shows robust effect
- Replication is working, but literature inflated

**Recommendation:**
- Moderate confidence in effect
- Your study adds evidential value
- Emphasize replication importance
- Highlight differences from literature

**Example Wording:**
> "While p-curve analysis of the published literature showed limited evidential value, our pre-registered replication demonstrated a robust effect across analytical specifications (82% significant, IF = 0.24), suggesting the phenomenon is real but may be smaller than originally reported."

---

### Scenario 3: Evidential Value but Fragile Analysis

**Pattern:**
- P-Curve: Evidential value = YES
- Spec Curve: 50-70% significant OR inconsistent sign
- Multiverse: IF >0.4 OR SF >0.3

**Interpretation:** ✓⚠⚠ **EVIDENTIAL VALUE BUT FRAGILE**
- Something real in the literature
- Your analysis is highly sensitive to choices
- Effect may be moderated or conditional

**Recommendation:**
- Look for moderators
- Identify boundary conditions
- Results may be context-dependent
- Report fragility honestly

**Example Wording:**
> "P-curve analysis indicated evidential value in the literature (p < .001). However, specification curve analysis revealed substantial analytical fragility (58% of specifications significant), with results particularly sensitive to outlier treatment (identified as most influential choice). We recommend caution in generalizing these findings."

---

### Scenario 4: No Evidential Value and Fragile

**Pattern:**
- P-Curve: Evidential value = NO, possible p-hacking
- Spec Curve: <50% significant
- Multiverse: IF >0.6, SF >0.3

**Interpretation:** ✗✗✗ **WEAK OR NO EVIDENCE**
- Literature lacks evidential value
- Results not robust to analytical choices
- Effect likely unreliable

**Recommendation:**
- Low confidence
- Do not publish as positive finding
- Consider file-drawer decision
- Focus on methodology improvement

**Example Wording:**
> "Integrated robustness assessment revealed substantial concerns: p-curve analysis detected no evidential value in the published literature, specification curve analysis showed only 42% of specifications were significant with frequent sign reversals (SF = 0.38), and multiverse analysis indicated high fragility (IF = 0.64). We conclude current evidence does not support the proposed effect."

---

## Handling Conflicts Between Methods

### Conflict 1: P-Curve Says NO, but Spec Curve Says ROBUST

**Possible Explanations:**
1. **Publication bias in literature, but effect is real in your data**
   - Your study is better powered/designed
   - Literature is inflated but effect exists

2. **Your study is atypical**
   - Different population
   - Different operationalization
   - Moderator present

**Resolution:**
- Emphasize YOUR analysis as contribution
- Note literature limitations
- Call for more pre-registered replications
- Report both findings transparently

**Decision Rule:**
```
IF p_curve_evidential_value == NO:
    AND spec_curve_pct_sig > 0.85:
    AND multiverse_IF < 0.25:
    THEN:
        Interpretation = "Robust effect in current data,
                         but published literature questionable"
        Confidence = MODERATE
        Recommendation = "Report as replication with stronger evidence"
```

---

### Conflict 2: P-Curve Says YES, but Spec Curve Says FRAGILE

**Possible Explanations:**
1. **Effect is real but highly context-dependent**
   - Strong moderators
   - Boundary conditions

2. **Literature is heterogeneous**
   - Different labs finding effect under different conditions
   - Your operationalization matters

3. **Measurement issues**
   - Some measures capture effect, others don't

**Resolution:**
- Explore moderators systematically
- Identify which specifications work/don't work
- Look for patterns in influential choices
- Frame as boundary condition identification

**Decision Rule:**
```
IF p_curve_evidential_value == YES:
    AND spec_curve_pct_sig < 0.60:
    AND sign_fragility > 0.20:
    THEN:
        Interpretation = "Effect exists but is conditional"
        Confidence = MODERATE
        Recommendation = "Identify moderators and boundary conditions"
```

---

### Conflict 3: Spec Curve Robust, but Multiverse Fragile

**Possible Explanations:**
1. **Data processing matters more than model choice**
   - Outliers drive results
   - Missing data handling critical
   - Transformations important

2. **Specification curve tested narrower universe**
   - Multiverse includes more extreme choices
   - Different scope

**Resolution:**
- Identify which multiverse dimensions drive fragility
- Focus on defensible data processing
- May need to exclude unreasonable paths
- Report both analyses with explanation

**Decision Rule:**
```
IF spec_curve_pct_sig > 0.80:
    AND multiverse_IF > 0.40:
    THEN:
        Identify influential multiverse choices
        IF fragility driven by data_processing:
            THEN: Report with clear data processing justification
        ELIF fragility driven by model_specification:
            THEN: May indicate model-dependent effect
```

---

## Formal Integration Algorithm

### Step 1: Assess Each Method Independently

```python
def assess_pcurve(results):
    if results['evidential_value'] == True and results['power'] > 0.50:
        return 'STRONG'
    elif results['evidential_value'] == True:
        return 'MODERATE'
    else:
        return 'WEAK'

def assess_spec_curve(results):
    pct_sig = results['pct_significant']
    sign_consistent = results['sign_fragility'] < 0.10

    if pct_sig > 0.90 and sign_consistent:
        return 'ROBUST'
    elif pct_sig > 0.70:
        return 'MODERATE'
    elif pct_sig > 0.50:
        return 'FRAGILE'
    else:
        return 'NOT_ROBUST'

def assess_multiverse(results):
    IF = results['inferential_fragility']
    SF = results['sign_fragility']

    if IF < 0.20 and SF < 0.10:
        return 'LOW_FRAGILITY'
    elif IF < 0.40:
        return 'MODERATE_FRAGILITY'
    else:
        return 'HIGH_FRAGILITY'
```

### Step 2: Combine Assessments

```python
def integrate_assessments(pcurve_assessment, spec_assessment, multi_assessment):
    # Convert to numerical scores
    scores = {
        'pcurve': score_mapping[pcurve_assessment],
        'spec': score_mapping[spec_assessment],
        'multi': score_mapping[multi_assessment]
    }

    # Overall confidence
    if all(s >= 3 for s in scores.values()):
        return 'HIGH_CONFIDENCE'
    elif all(s >= 2 for s in scores.values()):
        return 'MODERATE_CONFIDENCE'
    elif any(s == 1 for s in scores.values()):
        return 'LOW_CONFIDENCE'
    else:
        return 'VERY_LOW_CONFIDENCE'
```

### Step 3: Generate Recommendation

```python
def generate_recommendation(overall_confidence, assessments):
    if overall_confidence == 'HIGH_CONFIDENCE':
        return {
            'conclusion': 'Strong support for effect',
            'publication': 'Suitable for publication',
            'application': 'Can inform practice',
            'caveats': 'Report all analyses'
        }
    elif overall_confidence == 'MODERATE_CONFIDENCE':
        return {
            'conclusion': 'Moderate support, some limitations',
            'publication': 'Publishable with discussion of fragility',
            'application': 'Use cautiously',
            'caveats': 'Identify boundary conditions'
        }
    elif overall_confidence == 'LOW_CONFIDENCE':
        return {
            'conclusion': 'Weak evidence',
            'publication': 'Consider as null result',
            'application': 'Not recommended',
            'caveats': 'Need more research'
        }
    else:
        return {
            'conclusion': 'No reliable evidence',
            'publication': 'File-drawer',
            'application': 'Do not use',
            'caveats': 'Methodology may need revision'
        }
```

---

## Reporting Standards

### Minimal Reporting (All Three Methods Used)

**Required Elements:**

1. **P-Curve:**
   - Number of studies
   - Evidential value determination (yes/no)
   - Full and half p-curve test results
   - Power estimate
   - Plot

2. **Specification Curve:**
   - Number of specifications
   - Percentage significant
   - Median effect and range
   - Plot with confidence bands
   - Most influential choices

3. **Multiverse:**
   - Number of analytical paths
   - Fragility metrics (IF, SF, VoE)
   - Median effect
   - Plot showing distribution
   - Most influential decisions

4. **Integration:**
   - Clear statement of overall conclusion
   - Discussion of any conflicts
   - Limitations acknowledged

### Example Methods Section

> **Integrated Robustness Assessment.** We conducted a comprehensive evaluation using three complementary methods. First, we performed p-curve analysis (Simonsohn et al., 2014) on 23 published studies to assess evidential value in the literature. Second, we tested robustness of our primary finding using specification curve analysis (Simonsohn et al., 2020), systematically varying analytical choices across 120 specifications. Third, we quantified analytical fragility using multiverse analysis (Steegen et al., 2016), exploring 480 analytical paths varying data processing, model specification, and inferential decisions. All analyses were conducted using RobustStat v0.1.0 (Python). Code and data are available at [OSF link].

---

## Checklist for Researchers

Before claiming a "robust effect," ensure:

- [ ] P-curve analysis shows evidential value (if applicable)
- [ ] >80% of specifications significant
- [ ] Inferential fragility <0.30
- [ ] Sign fragility <0.15
- [ ] Results not driven by single analytical choice
- [ ] Effect size meaningful (not just significant)
- [ ] Replication considered (not just original finding)
- [ ] All analyses reported (even if conflicting)
- [ ] Limitations acknowledged
- [ ] Pre-registration (ideally)

---

## Final Recommendations

1. **Use all three methods when possible** - complementary evidence is strongest
2. **Report conflicts honestly** - don't cherry-pick
3. **Consider practical significance** - statistical robustness ≠ importance
4. **Update beliefs rationally** - weak evidence = weak conclusions
5. **Embrace uncertainty** - fragility is informative, not shameful

---

## References

- Simonsohn, U., Nelson, L. D., & Simmons, J. P. (2014). P-curve: A key to the file-drawer. *Journal of Experimental Psychology: General*, 143(2), 534-547.
- Simonsohn, U., Simmons, J. P., & Nelson, L. D. (2020). Specification curve analysis. *Nature Human Behaviour*, 4(11), 1208-1214.
- Steegen, S., Tuerlinckx, F., Gelman, A., & Vanpaemel, W. (2016). Increasing transparency through a multiverse analysis. *Perspectives on Psychological Science*, 11(5), 702-712.
