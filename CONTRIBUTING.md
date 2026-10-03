# Contributing
Use feat/<control>, fix/<issue>, or docs/<topic> branches. Use semantic commits such as feat(access): enforce clinic scopes. Open a pull request before merging; never merge directly into main. A reviewer checks least privilege, secret hygiene, privacy and test results. Required CI must pass. No live patient data or credentials are permitted in fixtures.

Use semantic versioning: major for incompatible interfaces, minor for compatible features, patch for fixes. Release by reviewed pull request, green CI, changelog and signed version tag; inject secrets through the deployment secret store and verify TLS at ingress. Protect main with required review and CI in GitHub settings. Remote PRs and protection settings require repository access.
