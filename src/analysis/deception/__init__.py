#!/usr/bin/env python3

"""Deception detection and evasiveness analysis"""
from src.analysis.deception.detector import DeceptionRiskAnalyzer, DeceptionRiskScore, DeceptionIndicators
from src.analysis.deception.linguistic_markers import LinguisticDeceptionMarkers
from src.analysis.deception.question_evasion import QuestionEvasionDetector, QuestionResponse
from src.analysis.deception.evasiveness import EvasivenessAnalyzer, EvasivenessScores

__all__ = [
	'DeceptionRiskAnalyzer',
	'DeceptionRiskScore',
	'DeceptionIndicators',
	'LinguisticDeceptionMarkers',
	'QuestionEvasionDetector',
	'QuestionResponse',
	'EvasivenessAnalyzer',
	'EvasivenessScores'
]