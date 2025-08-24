module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',     // New feature
        'fix',      // Bug fix
        'docs',     // Documentation
        'style',    // Formatting, missing semi colons, etc
        'refactor', // Code change that neither fixes a bug nor adds a feature
        'perf',     // Performance improvements
        'test',     // Adding missing tests
        'chore',    // Maintenance
        'ci',       // CI related changes
        'build',    // Build system changes
        'revert'    // Revert a commit
      ]
    ],
    'subject-case': [2, 'never', ['upper-case']]
  }
};