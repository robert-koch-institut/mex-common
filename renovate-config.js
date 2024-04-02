module.exports = {
    branchPrefix: 'test-renovate/',
    username: 'renovate-release',
    gitAuthor: 'Renovate Bot <bot@renovateapp.com>',
    onboarding: false,
    platform: 'github',
    includeForks: false,
    dryRun: 'full',
    repositories: ['robert-koch-institut/mex-common'],
    packageRules: [
        {
            description: 'lockFileMaintenance',
            matchUpdateTypes: [
                'pin',
                'digest',
                'patch',
                'minor',
                'major',
                'lockFileMaintenance',
            ],
            dependencyDashboardApproval: false,
            stabilityDays: 0,
        },
    ],
};
