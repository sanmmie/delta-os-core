/// Validation and serialization for DeltaOS integration manifests.
library delta_os_core.manifest_validator;

class DeltaManifest {
  const DeltaManifest({
    required this.version,
    required this.name,
    required this.description,
    required this.domains,
    required this.configuration,
    required this.dependencies,
    required this.ethicalConstraints,
  });

  factory DeltaManifest.fromJson(Map<String, dynamic> json) => DeltaManifest(
        version: json['version'] as String? ?? '',
        name: json['name'] as String? ?? '',
        description: json['description'] as String? ?? '',
        domains: List<String>.from(json['domains'] as List<dynamic>? ?? const []),
        configuration: Map<String, dynamic>.from(
          json['configuration'] as Map<dynamic, dynamic>? ?? const {},
        ),
        dependencies: (json['dependencies'] as List<dynamic>? ?? const [])
            .map((item) => Dependency.fromJson(Map<String, dynamic>.from(item as Map)))
            .toList(growable: false),
        ethicalConstraints: ManifestEthicalConstraints.fromJson(
          Map<String, dynamic>.from(
            json['ethicalConstraints'] as Map<dynamic, dynamic>? ?? const {},
          ),
        ),
      );

  final String version;
  final String name;
  final String description;
  final List<String> domains;
  final Map<String, dynamic> configuration;
  final List<Dependency> dependencies;
  final ManifestEthicalConstraints ethicalConstraints;

  Map<String, dynamic> toJson() => {
        'version': version,
        'name': name,
        'description': description,
        'domains': domains,
        'configuration': configuration,
        'dependencies': dependencies.map((item) => item.toJson()).toList(),
        'ethicalConstraints': ethicalConstraints.toJson(),
      };

  List<ValidationError> validate() {
    final errors = <ValidationError>[];
    if (!_isSemanticVersion(version)) {
      errors.add(const ValidationError(
        field: 'version', message: 'Version must follow semantic versioning.', code: 'INVALID_VERSION_FORMAT'));
    }
    if (name.trim().isEmpty) {
      errors.add(const ValidationError(field: 'name', message: 'Name must not be empty.', code: 'MISSING_NAME'));
    }
    if (domains.isEmpty) {
      errors.add(const ValidationError(field: 'domains', message: 'At least one domain is required.', code: 'MISSING_DOMAINS'));
    }
    for (final domain in domains) {
      if (!RegExp(r'^[a-z][a-z0-9_]*$').hasMatch(domain)) {
        errors.add(ValidationError(field: 'domains', message: 'Invalid domain format: $domain.', code: 'INVALID_DOMAIN_FORMAT'));
      }
    }
    errors.addAll(_validateDependencies(dependencies));
    return errors;
  }
}

class Dependency {
  const Dependency({required this.name, required this.version, required this.type});

  factory Dependency.fromJson(Map<String, dynamic> json) => Dependency(
        name: json['name'] as String? ?? '',
        version: json['version'] as String? ?? '',
        type: json['type'] as String? ?? '',
      );

  final String name;
  final String version;
  final String type;

  Map<String, String> toJson() => {'name': name, 'version': version, 'type': type};
}

class ManifestEthicalConstraints {
  const ManifestEthicalConstraints({this.frameworks = const {}});

  factory ManifestEthicalConstraints.fromJson(Map<String, dynamic> json) =>
      ManifestEthicalConstraints(frameworks: Set<String>.from(json['frameworks'] as List<dynamic>? ?? const []));

  final Set<String> frameworks;

  Map<String, dynamic> toJson() => {'frameworks': frameworks.toList()};
}

class ValidationError {
  const ValidationError({required this.field, required this.message, required this.code});

  final String field;
  final String message;
  final String code;
}

class ValidationResult {
  const ValidationResult({required this.isValid, required this.errors, required this.warnings});

  final bool isValid;
  final List<ValidationError> errors;
  final List<String> warnings;
}

class ManifestValidator {
  static const _supportedVersions = {'1.0.0', '1.1.0', '2.0.0-alpha'};
  static const _requiredFramework = 'universal_declaration_of_human_rights';

  static ValidationResult validateManifest(DeltaManifest manifest) {
    final errors = manifest.validate();
    if (!_supportedVersions.contains(manifest.version)) {
      errors.add(ValidationError(
        field: 'version', message: 'Unsupported manifest version: ${manifest.version}.', code: 'UNSUPPORTED_VERSION'));
    }
    if (!manifest.ethicalConstraints.frameworks.contains(_requiredFramework)) {
      errors.add(const ValidationError(
        field: 'ethicalConstraints.frameworks',
        message: 'The universal human rights framework is required.',
        code: 'MISSING_REQUIRED_ETHICAL_FRAMEWORK'));
    }
    return ValidationResult(
      isValid: errors.isEmpty,
      errors: List.unmodifiable(errors),
      warnings: manifest.description.trim().isEmpty ? const ['A manifest description is recommended.'] : const [],
    );
  }
}

List<ValidationError> _validateDependencies(List<Dependency> dependencies) {
  final errors = <ValidationError>[];
  const validTypes = {'required', 'optional', 'conflicting'};
  final names = <String>{};
  for (final dependency in dependencies) {
    if (dependency.name.trim().isEmpty) {
      errors.add(const ValidationError(
        field: 'dependencies.name', message: 'Dependency name must not be empty.', code: 'MISSING_DEPENDENCY_NAME'));
    } else if (!names.add(dependency.name)) {
      errors.add(ValidationError(
        field: 'dependencies', message: 'Dependency is declared more than once: ${dependency.name}.', code: 'DUPLICATE_DEPENDENCY'));
    }
    if (!_isSemanticVersion(dependency.version)) {
      errors.add(ValidationError(
        field: 'dependencies.version', message: 'Invalid dependency version: ${dependency.version}.', code: 'INVALID_DEPENDENCY_VERSION'));
    }
    if (!validTypes.contains(dependency.type)) {
      errors.add(ValidationError(
        field: 'dependencies.type', message: 'Invalid dependency type: ${dependency.type}.', code: 'INVALID_DEPENDENCY_TYPE'));
    }
  }
  return errors;
}

bool _isSemanticVersion(String value) => RegExp(
      r'^\d+\.\d+\.\d+(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$',
    ).hasMatch(value);
