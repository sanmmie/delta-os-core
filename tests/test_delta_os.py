import unittest

from delta_net_async import (
    DeltaOS,
    StateMachine,
    DeltaEngine,
    IntentIntegrator,
    Modules,
    Transmission,
    ContextCompiler,
    CompiledContext,
    EthicsEngine,
    IntuitionModule,
    EmotionModule,
    SymbolicInterface,
    TransformationPlan,
    InvalidTransitionError,
)


class TestStateMachine(unittest.TestCase):
    def setUp(self):
        self.sm = StateMachine()

    def test_initial_state_is_idle(self):
        self.assertEqual(self.sm.state, "idle")

    def test_idle_to_observe(self):
        result = self.sm.transition("on_input_signal")
        self.assertEqual(result, "observe")

    def test_full_cycle(self):
        events = ["on_input_signal", "on_delta_detected", "on_transformation_ready",
                   "on_action_complete", "on_feedback_processed", "on_cycle_completion"]
        expected = ["observe", "compute", "act", "reflect", "evolve", "idle"]
        for event, exp in zip(events, expected):
            self.assertEqual(self.sm.transition(event), exp)

    def test_invalid_transition_raises(self):
        with self.assertRaises(InvalidTransitionError):
            self.sm.transition("on_delta_detected")

    def test_can_handle(self):
        self.assertTrue(self.sm.can_handle("on_input_signal"))
        self.assertFalse(self.sm.can_handle("on_delta_detected"))
        self.sm.transition("on_input_signal")
        self.assertTrue(self.sm.can_handle("on_delta_detected"))

    def test_reset(self):
        self.sm.transition("on_input_signal")
        self.sm.reset()
        self.assertEqual(self.sm.state, "idle")

    def test_history_recorded(self):
        self.sm.transition("on_input_signal")
        history = self.sm.get_transition_log()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["from"], "idle")
        self.assertEqual(history[0]["to"], "observe")
        self.assertIn("event", history[0])
        self.assertIn("timestamp", history[0])


class TestDeltaEngine(unittest.TestCase):
    def setUp(self):
        self.engine = DeltaEngine(sensitivity=0.02)

    def test_compute_delta_up(self):
        result = self.engine.compute_delta(
            {"market_index": 105.0},
            [{"market_index": 100.0}],
        )
        self.assertAlmostEqual(result["delta"], 5.0)
        self.assertAlmostEqual(result["normalized"], 0.05)

    def test_compute_delta_down(self):
        result = self.engine.compute_delta(
            {"market_index": 95.0},
            [{"market_index": 100.0}],
        )
        self.assertAlmostEqual(result["delta"], -5.0)
        self.assertAlmostEqual(result["normalized"], -0.05)

    def test_compute_delta_no_history(self):
        result = self.engine.compute_delta({"market_index": 100.0}, [])
        self.assertAlmostEqual(result["delta"], 0.0)

    def test_generate_transformation_map_increase(self):
        delta = {"normalized": 0.1, "delta": 10.0, "prev": 100.0, "curr": 110.0}
        context = {"risk_tolerance": 0.5}
        plan = self.engine.generate_transformation_map(delta, context)
        self.assertEqual(plan.actions[0]["type"], "increase_allocation")
        self.assertGreater(plan.confidence, 0.0)
        self.assertLessEqual(plan.confidence, 0.95)

    def test_generate_transformation_map_hold(self):
        delta = {"normalized": 0.001, "delta": 0.1, "prev": 100.0, "curr": 100.1}
        plan = self.engine.generate_transformation_map(delta, {})
        self.assertEqual(plan.actions[0]["type"], "hold")

    def test_generate_transformation_map_decrease(self):
        delta = {"normalized": -0.05, "delta": -5.0, "prev": 100.0, "curr": 95.0}
        plan = self.engine.generate_transformation_map(delta, {})
        self.assertEqual(plan.actions[0]["type"], "decrease_allocation")


class TestIntentIntegrator(unittest.TestCase):
    def setUp(self):
        self.integrator = IntentIntegrator()

    def test_verify_intent_integrity_match(self):
        intent = {"actions": ["increase"]}
        plan = {"actions": [{"type": "increase_allocation"}]}
        self.assertTrue(self.integrator.verify_intent_integrity(intent, plan))

    def test_verify_intent_integrity_no_match(self):
        intent = {"actions": ["decrease"]}
        plan = {"actions": [{"type": "increase_allocation"}]}
        self.assertFalse(self.integrator.verify_intent_integrity(intent, plan))

    def test_verify_intent_integrity_no_actions(self):
        self.assertFalse(self.integrator.verify_intent_integrity({}, {}))

    def test_emit_intent_compliance_score(self):
        intent = {"priority": "high"}
        plan = {"actions": [{"type": "increase_allocation"}]}
        outcome = {"intent_score": 0.8, "plan": {"confidence": 0.9}}
        score = self.integrator.emit_intent_compliance_score(intent, plan, outcome)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_emit_intent_compliance_baseline(self):
        score = self.integrator.emit_intent_compliance_score({}, {}, None)
        self.assertAlmostEqual(score, 0.5)

    def test_map_outcome_to_intent(self):
        intent = {"priority": "high"}
        outcome = {"domain": "finance", "intent_score": 0.7, "plan": {"confidence": 0.8}}
        result = self.integrator.map_outcome_to_intent(outcome, intent)
        self.assertIn("alignment_score", result)
        self.assertIn("category", result)
        self.assertIn("intent", result)


class TestModulesObserve(unittest.TestCase):
    def setUp(self):
        self.modules = Modules()

    def test_observe_sensor(self):
        result = self.modules.observe({"temperature": 25.0, "pressure": 1.0}, channel="sensor")
        self.assertEqual(result["channel"], "sensor")
        self.assertIn("readings", result)
        self.assertEqual(result["readings"], [25.0, 1.0])

    def test_observe_text(self):
        result = self.modules.observe({"text": "hello world test"}, channel="text")
        self.assertEqual(result["channel"], "text")
        self.assertEqual(result["tokens"], ["hello", "world", "test"])

    def test_observe_audio(self):
        result = self.modules.observe({"waveform": [0.1, 0.2, 0.3]}, channel="audio")
        self.assertEqual(result["channel"], "audio")
        self.assertEqual(result["samples"], 3)

    def test_observe_api_stream(self):
        result = self.modules.observe({"endpoint": "/api/data", "status_code": 200}, channel="API_stream")
        self.assertEqual(result["channel"], "API_stream")
        self.assertEqual(result["endpoint"], "/api/data")

    def test_observe_generic(self):
        result = self.modules.observe({"key": "value"}, channel="unknown")
        self.assertEqual(result["channel"], "unknown")
        self.assertIn("pattern_map", result)

    def test_observe_records_history(self):
        self.modules.observe({"value": 1}, channel="sensor")
        self.assertEqual(len(self.modules.history), 1)
        self.assertEqual(self.modules.history[0]["channel"], "sensor")
        self.assertIn("timestamp", self.modules.history[0])

    def test_reflect(self):
        record = {
            "plan": {"actions": [{"type": "hold"}], "confidence": 0.8},
            "intent_score": 0.7,
            "delta_info": {"delta": 0.05},
        }
        result = self.modules.reflect(record)
        self.assertTrue(result["success"])
        self.assertIn("notes", result)
        self.assertIn("memory_trace", result)
        self.assertIn("evolution_signal", result)

    def test_reflect_low_confidence(self):
        record = {
            "plan": {"actions": [], "confidence": 0.1},
            "intent_score": 0.2,
            "delta_info": {"delta": 0.0},
        }
        result = self.modules.reflect(record)
        self.assertFalse(result["success"])


class TestTransmission(unittest.TestCase):
    def setUp(self):
        self.t = Transmission()

    def test_register_node(self):
        class FakeSig:
            def summary(self):
                return {"domain": "test"}
        self.t.register_node("node1", FakeSig())
        self.assertIn("node1", self.t.nodes)

    def test_sync_context(self):
        self.t.nodes = {"a": {"x": 1}, "b": {"y": 2}}
        result = self.t.sync_context("a", "b")
        self.assertEqual(result, {"x": 1, "y": 2})

    def test_quarantine(self):
        self.t.register_node("node1", type("S", (), {"summary": staticmethod(lambda: {})})())
        result = self.t.quarantine_corrupted_nodes("node1")
        self.assertEqual(result["status"], "quarantined")
        self.assertNotIn("node1", self.t.nodes)
        self.assertTrue(self.t.is_quarantined("node1"))

    def test_hash_context_signature(self):
        sig = self.t.hash_context_signature({"key": "value"})
        self.assertEqual(len(sig), 64)

    def test_verify_intent_alignment(self):
        intent = {"priority": "test"}
        plan = {"actions": [{"type": "hold"}]}
        result = self.t.verify_intent_alignment(intent, plan)
        self.assertIn("aligned", result)
        self.assertIn("score", result)

    def test_log_evolutionary_feedback(self):
        cycle_record = {
            "cycle": 1,
            "intent_score": 0.7,
            "plan": {"confidence": 0.8},
        }
        feedback = {"success": True, "notes": "test"}
        entry = self.t.log_evolutionary_feedback("node1", cycle_record, feedback)
        self.assertIn("timestamp", entry)
        self.assertEqual(entry["node_id"], "node1")
        self.assertEqual(entry["cycle"], 1)
        self.assertIn("feedback", entry)
        self.assertEqual(len(self.t.feedback_log), 1)

    def test_is_quarantined(self):
        self.assertFalse(self.t.is_quarantined("unknown"))
        self.t.quarantined.add("node1")
        self.assertTrue(self.t.is_quarantined("node1"))


class TestContextCompiler(unittest.TestCase):
    def setUp(self):
        self.compiler = ContextCompiler()

    def test_compile(self):
        result = self.compiler.compile({"risk_tolerance": 0.7})
        self.assertIsInstance(result, CompiledContext)
        summary = result.summary()
        self.assertEqual(summary["risk_tolerance"], 0.7)
        self.assertIn("ts", summary)

    def test_signature(self):
        result = self.compiler.compile({"key": "value"})
        sig = result.signature()
        self.assertEqual(len(sig), 64)

    def test_compile_default_risk(self):
        result = self.compiler.compile({})
        self.assertEqual(result.summary()["risk_tolerance"], 0.5)


class TestEthicsEngine(unittest.TestCase):
    def setUp(self):
        self.ethics = EthicsEngine()

    def test_check_consent_granted(self):
        context = {"consent": True, "domain": "test"}
        intent = {"domains": ["finance"]}
        result = self.ethics.check_consent(context, intent)
        self.assertTrue(result["consent"])
        self.assertIn("record", result)

    def test_check_consent_denied(self):
        context = {"consent": False}
        intent = {"domains": ["finance"]}
        result = self.ethics.check_consent(context, intent)
        self.assertFalse(result["consent"])

    def test_check_consent_default_granted(self):
        context = {}
        intent = {"domains": ["finance"]}
        result = self.ethics.check_consent(context, intent)
        self.assertTrue(result["consent"])

    def test_check_reciprocity_pass(self):
        plan = {"actions": [{"type": "increase_allocation"}]}
        result = self.ethics.check_reciprocity("node1", plan, ["node1", "node2"])
        self.assertTrue(result["reciprocal"])

    def test_check_reciprocity_fail_no_network(self):
        plan = {"actions": [{"type": "increase_allocation"}]}
        result = self.ethics.check_reciprocity("node1", plan, ["node1"])
        self.assertFalse(result["reciprocal"])

    def test_check_reciprocity_fail_no_benefit(self):
        plan = {"actions": [{"type": "decrease_allocation"}]}
        result = self.ethics.check_reciprocity("node1", plan, ["node1", "node2"])
        self.assertFalse(result["reciprocal"])

    def test_check_transparency_pass(self):
        plan = {"actions": [{"type": "hold"}], "rationale": "market trending up"}
        result = self.ethics.check_transparency("market trending up", plan)
        self.assertTrue(result["transparent"])

    def test_check_transparency_fail(self):
        plan = {"actions": [{"type": "hold"}]}
        result = self.ethics.check_transparency("", plan)
        self.assertFalse(result["transparent"])

    def test_evaluate_full_pass(self):
        context = {"consent": True}
        intent = {"domains": ["finance"]}
        plan = {"actions": [{"type": "hold"}], "rationale": "stable"}
        result = self.ethics.evaluate(context, intent, "node1", plan, ["node1", "node2"])
        self.assertTrue(result["passed"])
        self.assertIn("consent", result)
        self.assertIn("reciprocity", result)
        self.assertIn("transparency", result)

    def test_evaluate_fail(self):
        context = {}
        intent = {"domains": ["finance"]}
        result = self.ethics.evaluate(context, intent, "node1", {}, ["node1"])
        self.assertFalse(result["passed"])

    def test_ethics_logs(self):
        context = {"consent": True}
        intent = {"domains": ["finance"]}
        plan = {"actions": [{"type": "hold"}], "rationale": "stable"}
        self.ethics.evaluate(context, intent, "node1", plan, ["node1", "node2"])
        self.assertEqual(len(self.ethics.consent_log), 1)
        self.assertEqual(len(self.ethics.reciprocity_log), 1)
        self.assertEqual(len(self.ethics.transparency_log), 1)


class TestIntuitionModule(unittest.TestCase):
    def setUp(self):
        self.intuition = IntuitionModule()

    def test_suggest_with_history(self):
        history = [
            {"market_index": 100},
            {"market_index": 101},
            {"market_index": 102},
        ]
        result = self.intuition.suggest({}, history)
        self.assertEqual(result["type"], "predictive")
        self.assertIn("suggested_action", result)
        self.assertGreater(result["confidence"], 0.0)

    def test_suggest_no_history(self):
        result = self.intuition.suggest({}, [])
        self.assertEqual(result["suggested_action"], "hold")
        self.assertEqual(result["confidence"], 0.0)

    def test_suggest_partial_data(self):
        result = self.intuition.suggest({}, [], partial_data={"temp": 0.9})
        self.assertIn("partial_insights", result)

    def test_predictions_accumulate(self):
        history = [{"market_index": 100}, {"market_index": 102}]
        self.intuition.suggest({}, history)
        self.intuition.suggest({}, history)
        self.assertEqual(len(self.intuition.predictions), 2)


class TestEmotionModule(unittest.TestCase):
    def setUp(self):
        self.emotion = EmotionModule()

    def test_analyze_default(self):
        result = self.emotion.analyze()
        self.assertEqual(result["satisfaction"], 0.5)
        self.assertEqual(result["dominant_emotion"], "neutral")

    def test_analyze_with_sentiment(self):
        result = self.emotion.analyze(sentiment_data={"positive": 0.8, "trust": 0.9})
        self.assertEqual(result["satisfaction"], 0.8)
        self.assertEqual(result["trust"], 0.9)

    def test_analyze_with_feedback(self):
        result = self.emotion.analyze(user_feedback={"score": 0.7, "type": "positive"})
        self.assertEqual(result["satisfaction"], 0.7)
        self.assertEqual(result["dominant_emotion"], "positive")

    def test_affective_history(self):
        self.emotion.analyze()
        self.emotion.analyze(sentiment_data={"positive": 0.9})
        self.assertEqual(len(self.emotion.affective_history), 2)


class TestSymbolicInterface(unittest.TestCase):
    def setUp(self):
        self.interface = SymbolicInterface()

    def test_parse_symbolic_input(self):
        tokens = self.interface.parse_symbolic_input("Δ_market ©_context")
        symbol_tokens = [t for t in tokens if t["type"] == "symbol"]
        self.assertEqual(len(symbol_tokens), 2)
        self.assertEqual(symbol_tokens[0]["value"], "Δ")
        self.assertEqual(symbol_tokens[1]["value"], "©")

    def test_translate_to_action_code(self):
        tokens = self.interface.parse_symbolic_input("Δ test")
        action = self.interface.translate_to_action_code(tokens)
        self.assertIn("operations", action)
        self.assertIn("action_sequence", action)
        self.assertEqual(action["operations"][0], "observe")

    def test_assign_semantic_weights(self):
        tokens = self.interface.parse_symbolic_input("Δ")
        weighted = self.interface.assign_semantic_weights(tokens)
        self.assertEqual(weighted[0]["semantic_weight"], 0.9)


class TestDeltaOS(unittest.TestCase):
    def setUp(self):
        self.intent = {"priority": "restoration", "domains": ["healing"]}
        self.context = {"risk_tolerance": 0.3}
        self.os = DeltaOS(self.context, self.intent)

    def test_initialization(self):
        self.assertEqual(self.os.intent, self.intent)
        self.assertEqual(self.os.context, self.context)
        self.assertIsInstance(self.os.ethics, EthicsEngine)
        self.assertEqual(self.os.state, "idle")
        self.assertEqual(len(self.os.cycle_log), 0)

    def test_state_idle_initially(self):
        self.assertEqual(self.os.state, "idle")

    def test_init_node(self):
        context = self.os.init_node("node1", {"risk_tolerance": 0.5})
        self.assertIsInstance(context, CompiledContext)
        self.assertIn("node1", self.os.transmission.nodes)

    def test_transform_advances_state(self):
        result = self.os.transform({"market_index": 105.0}, {"risk_tolerance": 0.3})
        self.assertIn("state", result)
        self.assertEqual(result["state"], "compute")

    def test_run_cycle_with_consent(self):
        raw_env = {"risk_tolerance": 0.3, "consent": True}
        record, feedback = self.os.run_cycle(
            {"market_index": 105.0}, raw_env, node_id="node1"
        )
        self.assertIn("timestamp", record)
        self.assertIn("plan", record)
        self.assertIn("intent_score", record)
        self.assertIn("success", feedback)
        self.assertEqual(self.os.state, "idle")

    def test_run_cycle_without_consent(self):
        raw_env = {"risk_tolerance": 0.3, "consent": False}
        with self.assertRaises(PermissionError):
            self.os.run_cycle({"market_index": 105.0}, raw_env, node_id="node1")

    def test_run_cycle_default_consent_granted(self):
        raw_env = {"risk_tolerance": 0.3}
        record, feedback = self.os.run_cycle(
            {"market_index": 105.0}, raw_env, node_id="node1"
        )
        self.assertIn("timestamp", record)

    def test_evolve_no_cycles(self):
        result = self.os.evolve()
        self.assertEqual(result["status"], "no_cycles")

    def test_evolve_with_cycles(self):
        raw_env = {"risk_tolerance": 0.3, "consent": True}
        for i in range(3):
            self.os.run_cycle(
                {"market_index": 100.0 + i}, raw_env, node_id="node1"
            )
        result = self.os.evolve()
        self.assertEqual(result["status"], "evolved")
        self.assertIn("evolution", result)

    def test_evolve_transitions_to_idle(self):
        raw_env = {"risk_tolerance": 0.3, "consent": True}
        # Manually set state to evolve to simulate post-cycle state
        self.os.state_machine.current_state = "evolve"
        self.os.run_cycle({"market_index": 100.0}, raw_env, node_id="node1")
        # After run_cycle, state should be idle (evolve → idle transition)
        self.assertEqual(self.os.state, "idle")

    def test_evolve_logs_feedback(self):
        raw_env = {"risk_tolerance": 0.3, "consent": True}
        self.os.run_cycle({"market_index": 100.0}, raw_env, node_id="node1")
        result = self.os.evolve()
        self.assertEqual(result["status"], "evolved")
        self.assertGreater(len(self.os.transmission.feedback_log), 0)
        self.assertEqual(
            self.os.transmission.feedback_log[-1]["node_id"], "delta-core"
        )

    def test_cycle_log(self):
        raw_env = {"risk_tolerance": 0.3, "consent": True}
        self.os.run_cycle({"market_index": 100.0}, raw_env, node_id="node1")
        self.assertEqual(len(self.os.cycle_log), 1)
        self.assertEqual(self.os.cycle_log[0]["cycle"], 1)


if __name__ == "__main__":
    unittest.main()
