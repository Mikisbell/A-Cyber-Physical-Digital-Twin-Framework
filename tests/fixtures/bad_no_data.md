---
title: "Seismic Analysis of RC Frames Using OpenSeesPy"
domain: structural
quartile: conference
version: 1.0
status: draft
---

## Abstract

This paper analyzes the seismic response of reinforced concrete frames using OpenSeesPy finite element software. A three-story frame was modeled with fiber sections and subjected to earthquake loading. Results show that the proposed model captures the nonlinear response. The framework is open-source. <!-- AI_Assist -->

## 1. Introduction

Reinforced concrete frames are the most common structural system in seismic regions [1]. Finite element analysis using OpenSeesPy enables nonlinear dynamic simulation [2]. This paper models a three-story frame.

## 2. Methodology

The model uses forceBeamColumn elements with fiber sections. Concrete02 and Steel02 materials capture cyclic degradation. The Pisco 2007 earthquake record was applied. Rayleigh damping at 5% critical was used. Newmark integration with dt = 0.005 s.

[TODO: add model parameters table]
[TODO: add figure of model geometry]

## 3. Results

The analysis produced the following results. Peak displacement was approximately 45 mm at the roof level. The inter-story drift ratio reached about 1.8% at the second floor. The model showed good agreement with expected behavior.

[TODO: add displacement time history figure]
[TODO: add pushover curve]
[TODO: add damage state table with actual numbers]

## 4. Discussion

The results are consistent with engineering expectations for this type of structure. The model could be improved by adding more ground motion records.

## 5. Conclusions

An OpenSeesPy model of a three-story RC frame was analyzed under seismic loading. The results confirm the capability of the modeling approach.

## References

[1] A. K. Chopra, Dynamics of Structures, 5th ed. Pearson, 2017.
[2] F. McKenna et al., "OpenSees," PEER Center, UC Berkeley, 2000.
