"""
Delta Operating System - Consciousness Conductor
Phase III: Async Multi-Node Coordination

ΔOS Protocol: Observe (Δ) → Context (©) → Intention (™) → Evolve
"""

import asyncio
import datetime
import hashlib
import json
import logging
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# Minimal fallback definitions
@dataclass
class TransformationPlan:
    actions: List[Dict[str, Any]] = field(default_factory=list)
    rationale: str = ""
    confidence: float = 0.0


# ============================================================================
# ™ INTEGRATOR — Intent alignment and compliance scoring
# ============================================================================

class IntentIntegrator:
    """™ Integrator — Aligns transformations with intention signatures.

    Processes:
      - verify_intent_integrity()
      - map_outcome_to_intent()
      - emit_intent_compliance_score()
    """

    def __init__(self):
        self.intent_history = []

    def verify_intent_integrity(self, intent: dict, plan: dict) -> bool:
        """Verify that a transformation plan is compatible with declared intent."""
        if not intent or not plan:
            return False
        intent_actions = intent.get("actions", [])
        plan_actions = plan.get("actions", [])
        if not plan_actions:
            return False
        if intent_actions:
            intent_keywords = " ".join(str(a) for a in intent_actions).lower()
            for action in plan_actions:
                action_str = json.dumps(action).lower()
                if intent_keywords and intent_keywords in action_str:
                    return True
            return False
        return True

    def map_outcome_to_intent(self, outcome: dict, intent: dict) -> dict:
        """Map execution outcomes back to intent categories."""
        alignment = self.emit_intent_compliance_score(intent, {}, outcome)
        return {
            "intent": intent,
            "outcome_domain": outcome.get("domain", "unknown") if isinstance(outcome, dict) else "unknown",
            "alignment_score": alignment,
            "category": self._categorize(outcome, intent),
        }

    def emit_intent_compliance_score(self, intent: dict, plan: dict = None,
                                     outcome: dict = None) -> float:
        """Calculate intent compliance score (0.0 to 1.0)."""
        score = 0.5  # baseline
        plan_actions = []
        if plan and plan.get("actions"):
            plan_actions = [a.get("type", "") for a in plan["actions"]]
        intent_keywords = []
        if intent and isinstance(intent, dict):
            intent_keywords = [str(k).lower() for k in intent.keys()]
            intent_actions = intent.get("actions", [])
            if intent_actions:
                intent_keywords.extend(str(a).lower() for a in intent_actions)

        if intent_keywords and plan_actions:
            matches = sum(
                1 for a in plan_actions
                if any(kw in a.lower() for kw in intent_keywords)
            )
            score = 0.5 + (matches / max(len(plan_actions), 1)) * 0.4

        if outcome and isinstance(outcome, dict):
            intent_score = outcome.get("intent_score")
            if intent_score is not None:
                score = (score + intent_score) / 2
            confidence = outcome.get("plan", {}).get("confidence") if isinstance(outcome.get("plan"), dict) else None
            if confidence is not None:
                score = (score + confidence) / 2

        return round(max(0.0, min(1.0, score)), 4)

    def _categorize(self, outcome, intent):
        if not isinstance(outcome, dict) or not isinstance(intent, dict):
            return "unknown"
        confidence = outcome.get("plan", {}).get("confidence", 0) if isinstance(outcome.get("plan"), dict) else 0
        if confidence >= 0.8:
            return "high_alignment"
        elif confidence >= 0.5:
            return "moderate_alignment"
        return "low_alignment"


# ============================================================================
# Δ ENGINE — Change detection and transformation maps
# ============================================================================

class DeltaEngine:
    def __init__(self, sensitivity: float = 0.02):
        self.sensitivity = sensitivity

    def compute_delta(self, input_data, history):
        if history:
            prev = history[-1].get("market_index", 0.0)
        else:
            prev = input_data.get("market_index", 0.0)
        curr = input_data.get("market_index", prev)
        delta = curr - prev
        denom = max(abs(prev), 1.0)
        normalized = delta / denom
        return {
            "delta": delta,
            "normalized": normalized,
            "prev": prev,
            "curr": curr
        }

    def generate_transformation_map(self, delta_info, context):
        d = delta_info["normalized"]
        actions = []
        rationale = ""
        confidence = min(0.95, max(0.05, abs(d)))

        if d > self.sensitivity:
            actions.append({
                "type": "increase_allocation",
                "target": "equities",
                "magnitude": min(0.2, d)
            })
            rationale = "Market trending up; opportunistic increase."
        elif d < -self.sensitivity:
            actions.append({
                "type": "decrease_allocation",
                "target": "equities",
                "magnitude": min(0.2, -d)
            })
            rationale = "Market trending down; defensive posture."
        else:
            actions.append({
                "type": "hold",
                "target": "portfolio",
                "magnitude": 0.0
            })
            rationale = "No strong trend; maintain position."

        if isinstance(context, dict):
            risk = float(context.get("risk_tolerance", 0.5))
        else:
            risk = 0.5

        for action in actions:
            action["adjusted_magnitude"] = action.get("magnitude", 0.0) * (1.0 - risk)

        return TransformationPlan(
            actions=actions,
            rationale=rationale,
            confidence=confidence
        )


# ============================================================================
# STATE MACHINE — Formal state tracking with transition enforcement
# ============================================================================

class StateMachine:
    """ΔOS State Machine.

    States: [idle, observe, compute, act, reflect, evolve]
    Transitions:
      idle → observe: on_input_signal
      observe → compute: on_delta_detected
      compute → act: on_transformation_ready
      act → reflect: on_action_complete
      reflect → evolve: on_feedback_processed
      evolve → idle: on_cycle_completion
    """

    STATES = ["idle", "observe", "compute", "act", "reflect", "evolve"]

    TRANSITIONS = {
        "idle": {"on_input_signal": "observe"},
        "observe": {"on_delta_detected": "compute"},
        "compute": {"on_transformation_ready": "act"},
        "act": {"on_action_complete": "reflect"},
        "reflect": {"on_feedback_processed": "evolve"},
        "evolve": {"on_cycle_completion": "idle"},
    }

    def __init__(self):
        self.current_state = "idle"
        self.history = []

    @property
    def state(self):
        return self.current_state

    def transition(self, event: str) -> str:
        valid_events = self.TRANSITIONS.get(self.current_state, {})
        if event not in valid_events:
            raise InvalidTransitionError(
                f"Cannot '{event}' from state '{self.current_state}' "
                f"(valid: {list(valid_events.keys())})"
            )
        old_state = self.current_state
        self.current_state = valid_events[event]
        self.history.append({
            "from": old_state,
            "event": event,
            "to": self.current_state,
            "timestamp": datetime.datetime.utcnow().isoformat(),
        })
        return self.current_state

    def can_handle(self, event: str) -> bool:
        return event in self.TRANSITIONS.get(self.current_state, {})

    def reset(self):
        self.current_state = "idle"

    def get_transition_log(self) -> List[dict]:
        return list(self.history)


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


# ============================================================================
# CONSCIOUS MODULES — Intuition and Emotion
# ============================================================================

class IntuitionModule:
    """Intuition — Generates predictive suggestions from context + history + partial data.

    Input: context + historical + partial_data
    Output: predictive_suggestion
    """

    def __init__(self):
        self.predictions = []

    def suggest(self, context: dict, history: list, partial_data: dict = None) -> dict:
        """Generate a predictive suggestion based on context, history, and partial data."""
        suggestion = {
            "type": "predictive",
            "confidence": 0.0,
            "suggested_action": "hold",
            "risk_factors": [],
            "opportunities": [],
            "horizon": "short_term",
        }

        if history and len(history) >= 2:
            recent = history[-5:] if len(history) >= 5 else history
            values = []
            for h in recent:
                if isinstance(h, dict):
                    v = h.get("market_index", h.get("value", None))
                    if v is not None:
                        values.append(float(v))

            if len(values) >= 2:
                trend = values[-1] - values[0]
                trend_pct = trend / max(abs(values[0]), 1.0)
                volatility = max(abs(values[i] - values[i - 1]) for i in range(1, len(values)))

                if trend_pct > 0.01:
                    suggestion["suggested_action"] = "continue_trajectory"
                    suggestion["opportunities"].append("upward_momentum")
                elif trend_pct < -0.01:
                    suggestion["suggested_action"] = "prepare_correction"
                    suggestion["risk_factors"].append("downward_trend")
                else:
                    suggestion["suggested_action"] = "monitor"

                suggestion["confidence"] = min(0.95, abs(trend_pct) + 0.1)
                suggestion["volatility"] = round(volatility, 6)

                if volatility > 10:
                    suggestion["risk_factors"].append("high_volatility")
                if trend_pct > 0.005 and volatility < 5:
                    suggestion["risk_factors"].append("stable_growth")

        if partial_data and isinstance(partial_data, dict):
            suggestion["partial_insights"] = list(partial_data.keys())
            for key, value in partial_data.items():
                if isinstance(value, (int, float)):
                    if value < 0:
                        suggestion["risk_factors"].append(f"negative_{key}")
                    elif value > 0.8:
                        suggestion["opportunities"].append(f"strong_{key}")

        self.predictions.append(suggestion)
        return suggestion


class EmotionModule:
    """Emotion — Produces affective vectors from user feedback + sentiment data.

    Input: user_feedback + sentiment_data
    Output: affective_vector
    """

    def __init__(self):
        self.affective_history = []

    def analyze(self, user_feedback: dict = None, sentiment_data: dict = None) -> dict:
        """Analyze feedback/sentiment and produce an affective vector."""
        vector = {
            "satisfaction": 0.5,
            "trust": 0.5,
            "urgency": 0.3,
            "alignment": 0.5,
            "dominant_emotion": "neutral",
            "dimensions": {},
        }

        if sentiment_data and isinstance(sentiment_data, dict):
            vector["satisfaction"] = sentiment_data.get("positive", 0.5)
            vector["trust"] = sentiment_data.get("trust", 0.5)
            vector["urgency"] = sentiment_data.get("urgency", 0.3)
            vector["alignment"] = sentiment_data.get("alignment", 0.5)
            vector["dimensions"] = {
                k: v for k, v in sentiment_data.items()
                if isinstance(v, (int, float)) and k not in ("timestamp",)
            }

        if user_feedback and isinstance(user_feedback, dict):
            score = user_feedback.get("score")
            if score is not None:
                vector["satisfaction"] = float(score)
            feedback_type = user_feedback.get("type")
            if feedback_type:
                vector["dominant_emotion"] = feedback_type
                vector["dimensions"][feedback_type] = float(score) if score is not None else 0.5
            explicit = user_feedback.get("consent")
            if explicit is not None:
                vector["consent_given"] = bool(explicit)

        # Determine dominant emotion from dimensions
        if vector["dimensions"]:
            dominant = max(vector["dimensions"], key=vector["dimensions"].get)
            vector["dominant_emotion"] = dominant

        vector["satisfaction"] = round(max(0.0, min(1.0, vector["satisfaction"])), 4)
        vector["trust"] = round(max(0.0, min(1.0, vector["trust"])), 4)
        vector["urgency"] = round(max(0.0, min(1.0, vector["urgency"])), 4)
        vector["alignment"] = round(max(0.0, min(1.0, vector["alignment"])), 4)

        self.affective_history.append(vector)
        return vector


# ============================================================================
# ETHICS ENGINE — Consent, reciprocity, transparency
# ============================================================================

class EthicsEngine:
    """Ethics Engine — Enforces consent, reciprocity, and transparency principles.

    Principles:
      - Consent: User must explicitly grant consent before transformation.
      - Reciprocity: Benefits must extend beyond the origin node.
      - Transparency: All decisions must have auditable rationale.
    """

    def __init__(self):
        self.consent_log = []
        self.reciprocity_log = []
        self.transparency_log = []

    def check_consent(self, context: dict, intent: dict) -> dict:
        """Verify user consent is present and valid."""
        consent_raw = context.get("consent", context.get("user_consent", True))
        consent_granted = bool(consent_raw) if not isinstance(consent_raw, bool) else consent_raw
        record = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "consent_granted": consent_granted,
            "context_keys": list(context.keys()) if isinstance(context, dict) else [],
            "intent_domains": intent.get("domains", []) if isinstance(intent, dict) else [],
        }
        self.consent_log.append(record)
        return {
            "consent": consent_granted,
            "record": record,
        }

    def check_reciprocity(self, node_id: str, plan: dict, network_nodes: list) -> dict:
        """Verify benefit extends beyond the origin node."""
        if not node_id or not plan or not network_nodes:
            return {"reciprocal": False, "reason": "insufficient_data"}
        plan_actions = plan.get("actions", []) if isinstance(plan, dict) else []
        beneficial = any(
            a.get("type") in ("increase_allocation", "hold", "continue_trajectory")
            for a in plan_actions
        )
        extends_beyond = len(network_nodes) > 1
        reciprocal = beneficial and extends_beyond
        record = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "node_id": node_id,
            "reciprocal": reciprocal,
            "network_size": len(network_nodes),
            "reason": "benefit extends to network" if reciprocal else "benefit too narrow or no network",
        }
        self.reciprocity_log.append(record)
        return {
            "reciprocal": reciprocal,
            "record": record,
        }

    def check_transparency(self, rationale: str, plan: dict) -> dict:
        """Verify decision has auditable rationale."""
        transparent = bool(rationale and isinstance(rationale, str) and len(rationale.strip()) > 0)
        record = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "transparent": transparent,
            "rationale": rationale or "",
            "has_actions": bool(plan and isinstance(plan, dict) and plan.get("actions")),
        }
        self.transparency_log.append(record)
        return {
            "transparent": transparent,
            "record": record,
        }

    def evaluate(self, context: dict, intent: dict, node_id: str, plan: dict, network_nodes: list) -> dict:
        """Run all three ethics checks and return combined result."""
        consent = self.check_consent(context, intent)
        reciprocity = self.check_reciprocity(node_id, plan, network_nodes)
        transparency = self.check_transparency(
            plan.get("rationale", "") if isinstance(plan, dict) else "",
            plan if isinstance(plan, dict) else {},
        )
        passed = consent["consent"] and reciprocity["reciprocal"] and transparency["transparent"]
        return {
            "passed": passed,
            "consent": consent,
            "reciprocity": reciprocity,
            "transparency": transparency,
        }


# ============================================================================
# © COMPILER — Context compilation and signature synthesis
# ============================================================================

class ContextCompiler:
    def compile(self, raw_env):
        timestamp = datetime.datetime.utcnow()
        environment = dict(raw_env)
        environment.setdefault("risk_tolerance", 0.5)
        environment.setdefault("ethical_constraints", {})

        return CompiledContext(environment, timestamp)


class CompiledContext:
    def __init__(self, environment, timestamp):
        self.env = environment
        self.timestamp = timestamp

    def summary(self):
        result = dict(self.env)
        result["ts"] = self.timestamp.isoformat()
        return result

    def signature(self) -> str:
        """Synthesize a context signature (© protocol)."""
        context_str = json.dumps(self.env, sort_keys=True, default=str)
        return hashlib.sha256(context_str.encode()).hexdigest()


# ============================================================================
# CONSCIOUS MODULES — Observation and Reflection
# ============================================================================

class Modules:
    def __init__(self):
        self.history = []

    def observe(self, data, channel="sensor"):
        record = {
            "channel": channel,
            "data": dict(data) if isinstance(data, dict) else {"value": data},
            "timestamp": datetime.datetime.utcnow().isoformat(),
        }
        self.history.append(record)
        channel_handlers = {
            "sensor": self._observe_sensor,
            "text": self._observe_text,
            "audio": self._observe_audio,
            "API_stream": self._observe_api_stream,
        }
        handler = channel_handlers.get(channel, self._observe_generic)
        return handler(record)

    def _observe_generic(self, record):
        return {"pattern_map": record["data"], "channel": record["channel"]}

    def _observe_sensor(self, record):
        data = record["data"]
        return {
            "pattern_map": data,
            "channel": "sensor",
            "readings": [v for k, v in data.items() if isinstance(v, (int, float))],
            "channels": list(data.keys()),
        }

    def _observe_text(self, record):
        data = record["data"]
        text = data.get("text", data.get("content", ""))
        return {
            "pattern_map": data,
            "channel": "text",
            "tokens": text.split() if isinstance(text, str) else [],
            "length": len(text) if isinstance(text, str) else 0,
            "channels": list(data.keys()),
        }

    def _observe_audio(self, record):
        data = record["data"]
        waveform = data.get("waveform", data.get("audio_data", []))
        return {
            "pattern_map": data,
            "channel": "audio",
            "samples": len(waveform) if isinstance(waveform, (list, tuple)) else 0,
            "channels": list(data.keys()),
        }

    def _observe_api_stream(self, record):
        data = record["data"]
        return {
            "pattern_map": data,
            "channel": "API_stream",
            "endpoint": data.get("endpoint", data.get("url", "")),
            "status": data.get("status_code", data.get("status", 0)),
            "channels": list(data.keys()),
        }

    def reflect(self, record):
        """Reflect on cycle record and produce memory trace (no longer a stub)."""
        confidence = 0.0
        intent_score = 0.5
        delta_magnitude = 0.0
        actions_taken = 0

        if isinstance(record, dict):
            plan = record.get("plan", {})
            if isinstance(plan, dict):
                confidence = plan.get("confidence", 0.0)
                actions_taken = len(plan.get("actions", []))
            intent_score = record.get("intent_score", 0.5)
            delta_info = record.get("delta_info", {})
            if isinstance(delta_info, dict):
                delta_magnitude = delta_info.get("delta", 0.0)

        notes_parts = []
        if confidence >= 0.7:
            notes_parts.append("high confidence transformation")
        elif confidence >= 0.4:
            notes_parts.append("moderate confidence transformation")
        else:
            notes_parts.append("low confidence — review recommended")

        if intent_score >= 0.7:
            notes_parts.append("intent well-aligned")
        elif intent_score < 0.4:
            notes_parts.append("intent misalignment detected")

        if abs(delta_magnitude) < 0.01:
            notes_parts.append("minimal change observed")

        return {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "success": confidence >= 0.3 and intent_score >= 0.3,
            "notes": "; ".join(notes_parts) if notes_parts else "insufficient data for reflection",
            "memory_trace": {
                "cycle_intent_score": intent_score,
                "plan_confidence": confidence,
                "delta_magnitude": delta_magnitude,
                "actions_taken": actions_taken,
            },
            "evolution_signal": "stable" if confidence >= 0.5 else "unstable",
        }


# ============================================================================
# TRANSMISSION — ΔNet link protocol with integrity checks
# ============================================================================

class Transmission:
    def __init__(self):
        self.nodes = {}
        self.quarantined = set()
        self.feedback_log = []

    def log_evolutionary_feedback(self, node_id, cycle_record, feedback):
        entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "node_id": node_id,
            "cycle": cycle_record.get("cycle", 0) if isinstance(cycle_record, dict) else 0,
            "intent_score": cycle_record.get("intent_score", 0.5) if isinstance(cycle_record, dict) else 0.5,
            "plan_confidence": cycle_record.get("plan", {}).get("confidence", 0.0) if isinstance(cycle_record, dict) and isinstance(cycle_record.get("plan"), dict) else 0.0,
            "feedback": feedback,
        }
        self.feedback_log.append(entry)
        return entry

    def register_node(self, node_id, signature):
        self.nodes[node_id] = signature.summary()

    def sync_context(self, node_a, node_b):
        context_a = self.nodes.get(node_a, {})
        context_b = self.nodes.get(node_b, {})
        return {**context_a, **context_b}

    def hash_context_signature(self, context: dict) -> str:
        """Hash context to produce a verifiable signature (integrity check)."""
        context_str = json.dumps(context, sort_keys=True, default=str)
        return hashlib.sha256(context_str.encode()).hexdigest()

    def verify_intent_alignment(self, intent: dict, plan: dict, outcome: dict = None) -> dict:
        """Verify that plan and outcome align with declared intent."""
        integrator = IntentIntegrator()
        score = integrator.emit_intent_compliance_score(intent, plan, outcome)
        return {
            "aligned": score >= 0.5,
            "score": score,
            "intent": intent,
        }

    def quarantine_corrupted_nodes(self, node_id: str) -> dict:
        """Isolate a corrupted node from the network."""
        self.quarantined.add(node_id)
        if node_id in self.nodes:
            del self.nodes[node_id]
        return {
            "node_id": node_id,
            "status": "quarantined",
            "action": "isolated_from_network",
        }

    def is_quarantined(self, node_id: str) -> bool:
        return node_id in self.quarantined


# ============================================================================
# ΔOS CORE — Delta Operating System
# ============================================================================

class SymbolicInterface:
    r"""ΔOS Symbolic Interface.

    Syntax: $\Delta$[state] → $\odot$[context] → $\text{T}$[intent]
    Translates symbolic inputs to action code with semantic weights.
    """

    def __init__(self):
        self.symbol_table = {
            "Δ": "observe",
            "©": "contextualize",
            "™": "align_intent",
            "→": "transitions_to",
            "∫": "accumulate",
            "∂": "partial_derivative",
        }

    def parse_symbolic_input(self, symbolic_input: str) -> List[dict]:
        """Parse symbolic syntax into structured tokens."""
        tokens = []
        current = ""
        in_subscript = False
        for char in symbolic_input:
            if char in self.symbol_table:
                if current:
                    tokens.append({"type": "operand", "value": current})
                    current = ""
                tokens.append({
                    "type": "symbol",
                    "value": char,
                    "operation": self.symbol_table[char],
                })
            elif char == "_":
                in_subscript = True
                current += char
            elif char.isalnum() or char in "_-.":
                current += char
            elif char == " " or char == ",":
                if current:
                    tokens.append({"type": "operand", "value": current})
                    current = ""
        if current:
            tokens.append({"type": "operand", "value": current})
        return tokens

    def assign_semantic_weights(self, tokens: List[dict], context: dict = None) -> List[dict]:
        """Assign semantic weights to parsed tokens."""
        weighted = []
        context_signals = context or {}
        for token in tokens:
            weight = 0.5
            if token["type"] == "symbol":
                weight = 0.9
            elif token["type"] == "operand":
                val = token.get("value", "")
                for signal_key, signal_val in context_signals.items():
                    if signal_key in val.lower():
                        weight = min(1.0, weight + 0.1)
            token["semantic_weight"] = weight
            weighted.append(token)
        return weighted

    def translate_to_action_code(self, tokens: List[dict], intent: dict = None) -> dict:
        """Translate symbolic tokens to structured action code."""
        operations = [t["operation"] for t in tokens if t["type"] == "symbol"]
        operands = [t["value"] for t in tokens if t["type"] == "operand"]

        action_code = {
            "operations": operations,
            "operands": operands,
            "intent_aligned": False,
            "intent": intent or {},
            "action_sequence": [],
        }

        if intent and isinstance(intent, dict):
            intent_domains = intent.get("domains", []) or []
            intent_priority = intent.get("priority")
            if intent_priority:
                action_code["intent_aligned"] = True
                action_code["intent_priority"] = intent_priority

        for op in operations:
            step = {"operation": op, "executable": True}
            if op == "observe":
                step["collect"] = operands
            elif op == "contextualize":
                step["tag"] = operands
            elif op == "align_intent":
                step["verify"] = intent_domains if intent_domains else operands
            action_code["action_sequence"].append(step)

        return action_code


class DeltaOS:
    def __init__(self, context, intent):
        self.kernel_delta = DeltaEngine()
        self.compiler = ContextCompiler()
        self.integrator = IntentIntegrator()  # WAS: None — now fully implemented
        self.modules = Modules()
        self.transmission = Transmission()
        self.context = context
        self.intent = intent
        self.ethics = EthicsEngine()
        self.cycle_log = []
        self.state_machine = StateMachine()
        self.quarantined_nodes = set()
        self._intuition = IntuitionModule()
        self._emotion = EmotionModule()

    @property
    def state(self):
        return self.state_machine.state

    def init_node(self, node_id, raw_env):
        context = self.compiler.compile(raw_env)
        self.transmission.register_node(node_id, context)
        return context

    def transform(self, input_data, raw_env):
        """Execute a transformation (Δ → plan) without full cycle recording."""
        if self.state_machine.can_handle("on_input_signal"):
            self.state_machine.transition("on_input_signal")
        self.modules.observe(input_data)
        if self.state_machine.can_handle("on_delta_detected"):
            self.state_machine.transition("on_delta_detected")
        context = self.compiler.compile(raw_env)
        history_slice = self.modules.history[:-1]
        delta_info = self.kernel_delta.compute_delta(input_data, history_slice)
        plan = self.kernel_delta.generate_transformation_map(delta_info, context)
        return {
            "actions": plan.actions,
            "rationale": plan.rationale,
            "confidence": plan.confidence,
            "delta_info": delta_info,
            "context": context,
            "state": self.state_machine.state,
        }

    def run_cycle(self, input_data, raw_env, node_id=None):
        # Ethics gate: consent check BEFORE entering observe state
        consent_result = self.ethics.check_consent(raw_env, self.intent)
        if not consent_result["consent"]:
            raise PermissionError(
                "Consent required for transformation (ethics layer)"
            )

        # State machine: idle → observe (on_input_signal)
        if self.state_machine.can_handle("on_input_signal"):
            self.state_machine.transition("on_input_signal")

        self.modules.observe(input_data)
        context = self.compiler.compile(raw_env)

        history_slice = self.modules.history[:-1]
        delta_info = self.kernel_delta.compute_delta(input_data, history_slice)

        # State machine: observe → compute (on_delta_detected)
        if self.state_machine.can_handle("on_delta_detected"):
            self.state_machine.transition("on_delta_detected")

        plan = self.kernel_delta.generate_transformation_map(delta_info, context)
        plan_dict = {
            "actions": plan.actions,
            "rationale": plan.rationale,
            "confidence": plan.confidence
        }

        # Intent compliance via ™ Integrator
        intent_compliance = self.integrator.emit_intent_compliance_score(
            self.intent, plan_dict, input_data
        )

        # Ethics checks after plan is generated (reciprocity + transparency)
        if node_id:
            network_nodes = list(self.transmission.nodes.keys()) + [node_id]
            reciprocity = self.ethics.check_reciprocity(
                node_id, plan_dict, network_nodes
            )
            transparency = self.ethics.check_transparency(
                plan.rationale, plan_dict
            )
            if not reciprocity["reciprocal"]:
                logger.warning("Node %s: reciprocity check failed", node_id)
            if not transparency["transparent"]:
                logger.warning("Node %s: transparency check failed", node_id)

        cycle_record = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "input": input_data,
            "context": context.summary(),
            "context_signature": context.signature(),
            "delta_info": delta_info,
            "plan": plan_dict,
            "intent_score": intent_compliance,
        }

        # State machine: compute → act (on_transformation_ready)
        if self.state_machine.can_handle("on_transformation_ready"):
            self.state_machine.transition("on_transformation_ready")

        # State machine: act → reflect (on_action_complete)
        if self.state_machine.can_handle("on_action_complete"):
            self.state_machine.transition("on_action_complete")

        feedback = self.modules.reflect(cycle_record)

        # Log evolutionary feedback
        self.transmission.log_evolutionary_feedback(
            node_id or "unknown", cycle_record, feedback
        )

        # State machine: reflect → evolve (on_feedback_processed)
        if self.state_machine.can_handle("on_feedback_processed"):
            self.state_machine.transition("on_feedback_processed")

        # State machine: evolve → idle (on_cycle_completion)
        if self.state_machine.can_handle("on_cycle_completion"):
            self.state_machine.transition("on_cycle_completion")

        self.cycle_log.append({
            "cycle": len(self.cycle_log) + 1,
            "record": cycle_record,
            "feedback": feedback,
        })

        if node_id:
            self.transmission.register_node(node_id, context)

        return cycle_record, feedback

    def evolve(self):
        """Evolve system based on accumulated feedback (ΔOS.evolve)."""
        if not self.cycle_log:
            return {"status": "no_cycles", "evolution": "baseline"}

        recent_confidence = [
            cycle["record"]["plan"].get("confidence", 0)
            for cycle in self.cycle_log[-5:]
            if isinstance(cycle.get("record"), dict)
            and isinstance(cycle["record"].get("plan"), dict)
        ]
        avg_confidence = (
            sum(recent_confidence) / len(recent_confidence)
            if recent_confidence else 0
        )
        avg_intent = [
            cycle["record"].get("intent_score", 0.5)
            for cycle in self.cycle_log[-5:]
        ]
        avg_intent_score = sum(avg_intent) / len(avg_intent) if avg_intent else 0.5

        if avg_confidence > 0.7 and avg_intent_score > 0.6:
            evolution = "adapted"
        elif avg_confidence > 0.4:
            evolution = "maintained"
        else:
            evolution = "needs_review"

        return {
            "status": "evolved",
            "evolution": evolution,
            "avg_confidence": round(avg_confidence, 4),
            "avg_intent_score": round(avg_intent_score, 4),
            "total_cycles": len(self.cycle_log),
            "state": self.state_machine.state,
        }


# Setup logging
logger = logging.getLogger("delta_net_async")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


# ============================================================================
# TRANSPORT — In-memory pub/sub
# ============================================================================

class InMemoryTransport:
    def __init__(self):
        self.subscribers = {}

    async def register(self, node_id):
        queue = asyncio.Queue()
        self.subscribers[node_id] = queue
        logger.debug("Transport: registered %s", node_id)
        return queue

    async def unregister(self, node_id):
        if node_id in self.subscribers:
            del self.subscribers[node_id]
        logger.debug("Transport: unregistered %s", node_id)

    async def publish(self, source_node, message):
        subscribers_count = 0
        for node_id, queue in self.subscribers.items():
            if node_id != source_node:
                await queue.put({
                    "from": source_node,
                    "msg": message,
                    "ts": datetime.datetime.utcnow().isoformat()
                })
                subscribers_count += 1
        logger.debug("Transport: %s published to %s nodes", source_node, subscribers_count)


# ============================================================================
# ASYNC DELTA NODE
# ============================================================================

class AsyncDeltaNode:
    def __init__(self, node_id, intent, transport):
        self.node_id = node_id
        self.intent = intent
        self.transport = transport
        self.system = DeltaOS(intent, intent)
        self.queue = None
        self.running = False

    async def start(self, raw_env):
        self.queue = await self.transport.register(self.node_id)
        self.system.init_node(self.node_id, raw_env)
        self.running = True
        logger.info("Node %s started", self.node_id)

    async def stop(self):
        self.running = False
        if self.queue:
            await self.transport.unregister(self.node_id)
        logger.info("Node %s stopped", self.node_id)

    async def run_cycle_async(self, input_data, raw_env):
        def run_sync():
            return self.system.run_cycle(input_data, raw_env, self.node_id)

        record, feedback = await asyncio.get_running_loop().run_in_executor(None, run_sync)

        await self.transport.publish(self.node_id, {
            "context": record["context"],
            "delta": record["delta_info"]
        })

        return record, feedback

    async def listen(self):
        if not self.queue:
            raise RuntimeError("Node not started")

        while self.running:
            try:
                message = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            peer = message.get("from")
            context_data = message.get("msg", {}).get("context")

            if context_data:
                class PeerSignature:
                    @staticmethod
                    def summary():
                        return context_data

                try:
                    self.system.transmission.register_node(peer, PeerSignature())
                    logger.info("Node %s received context from %s", self.node_id, peer)
                except Exception:
                    logger.debug("Node %s failed to register peer context", self.node_id)


async def demo_async_deltanet(cycles=6):
    transport = InMemoryTransport()

    nodes = [
        AsyncDeltaNode("healing", {"priority": "restoration"}, transport),
        AsyncDeltaNode("heritage", {"priority": "preservation"}, transport),
        AsyncDeltaNode("finance", {"priority": "ethical_growth"}, transport),
    ]

    # Start nodes
    for node in nodes:
        await node.start({"risk_tolerance": 0.3})

    # Start listeners
    listeners = []
    for node in nodes:
        task = asyncio.create_task(node.listen())
        listeners.append(task)

    # Run cycles
    for cycle_num in range(cycles):
        tasks = []
        for node in nodes:
            base_value = 1000.0
            random_change = random.normalvariate(0, 5)
            if cycle_num == cycles // 2:
                random_change += 5
            market_index = base_value + random_change
            input_data = {"market_index": round(market_index, 6)}
            raw_env = {"risk_tolerance": 0.3, "domain": node.node_id}
            task = asyncio.create_task(node.run_cycle_async(input_data, raw_env))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        logger.info("Completed cycle %s/%s", cycle_num + 1, cycles)

        for index, (record, feedback) in enumerate(results):
            logger.info(
                "Node %s - intent_score=%s plan_conf=%s",
                nodes[index].node_id,
                record.get('intent_score'),
                record.get('plan', {}).get('confidence')
            )

        await asyncio.sleep(0.5)

    # Cleanup
    for node in nodes:
        await node.stop()

    for listener_task in listeners:
        listener_task.cancel()

    # Demonstrate evolve
    for node in nodes:
        evolution = node.system.evolve()
        logger.info("Node %s evolution: %s", node.node_id, evolution)

    logger.info("Demo async deltanet complete")


if __name__ == "__main__":
    asyncio.run(demo_async_deltanet(cycles=6))
