import 'package:delta_os_core/delta_os_core.dart';
import 'package:test/test.dart';

void main() {
  test('accepts a complete supported manifest', () {
    final result = ManifestValidator.validateManifest(const DeltaManifest(
      version: '1.0.0',
      name: 'health-coordinator',
      description: 'Coordinates health actions.',
      domains: ['health'],
      configuration: {},
      dependencies: [Dependency(name: 'climate-signals', version: '1.0.0', type: 'optional')],
      ethicalConstraints: ManifestEthicalConstraints(
        frameworks: {'universal_declaration_of_human_rights'},
      ),
    ));
    expect(result.isValid, isTrue);
    expect(result.errors, isEmpty);
  });

  test('reports invalid manifest fields', () {
    final result = ManifestValidator.validateManifest(const DeltaManifest(
      version: 'bad-version',
      name: '',
      description: '',
      domains: ['Bad Domain'],
      configuration: {},
      dependencies: [Dependency(name: '', version: 'x', type: 'unknown')],
      ethicalConstraints: ManifestEthicalConstraints(),
    ));
    expect(result.isValid, isFalse);
    expect(result.errors.map((error) => error.code), containsAll([
      'INVALID_VERSION_FORMAT', 'MISSING_NAME', 'INVALID_DOMAIN_FORMAT',
      'MISSING_DEPENDENCY_NAME', 'INVALID_DEPENDENCY_VERSION',
      'INVALID_DEPENDENCY_TYPE', 'MISSING_REQUIRED_ETHICAL_FRAMEWORK',
    ]));
  });
}
