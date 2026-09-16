import 'package:test/test.dart';
import 'package:delta_os_core/core/orchestrator.dart';

void main() {
  group('Orchestrator Basic Tests', () {
    test('DomainAction creation works', () {
      final action = DomainAction(
        domain: 'climate',
        type: 'reduce_emissions',
      );

      expect(action.domain, 'climate');
      expect(action.type, 'reduce_emissions');
    });

    test('CoordinationContext creation works', () {
      final context = CoordinationContext();

      expect(context.environment, isEmpty);
      expect(context.ethicalConstraints.prohibitedActionTypes, isNotEmpty);
    });

    test('ActionPriority values exist', () {
      expect(ActionPriority.immediate, isNotNull);
      expect(ActionPriority.strategic, isNotNull);
      expect(ActionPriority.longTerm, isNotNull);
    });
  });

  group('Ethical Governance', () {
    test('EthicalConstraints has prohibited types', () {
      final constraints = EthicalConstraints();
      
      expect(constraints.prohibitedActionTypes, contains('exploitative'));
      expect(constraints.prohibitedActionTypes, contains('harmful'));
    });

    test('EthicalAudit creation works', () {
      final audit = EthicalAudit(
        isApproved: true,
        violations: [],
        auditedActions: 5,
      );

      expect(audit.isApproved, isTrue);
      expect(audit.violations, isEmpty);
    });
  });

  test('rejects prohibited actions', () async {
    await expectLater(
      Orchestrator().coordinate(
        proposedActions: [DomainAction(domain: 'health', type: 'harmful_experiment')],
        context: CoordinationContext(),
      ),
      throwsA(isA<EthicalConstraintException>()),
    );
  });

  test('orders immediate actions before strategic and long-term actions', () async {
    final result = await Orchestrator().coordinate(
      proposedActions: [
        DomainAction(domain: 'health', type: 'plan', priority: ActionPriority.longTerm),
        DomainAction(domain: 'climate', type: 'respond', priority: ActionPriority.immediate),
        DomainAction(domain: 'education', type: 'teach', priority: ActionPriority.strategic),
      ],
      context: CoordinationContext(),
    );
    expect(result.actions.map((action) => action.priority), [
      ActionPriority.immediate,
      ActionPriority.strategic,
      ActionPriority.longTerm,
    ]);
  });
}
