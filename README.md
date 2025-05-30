# RIDE Console - Monitoring and Admin Tools

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Lifecycle:Maturing](https://img.shields.io/badge/Lifecycle-Maturing-007EC6)](https://github.com/bcgov/repomountie/blob/master/doc/lifecycle-badges.md)

![Tests](https://github.com/bcgov/rsbc-ride-console/workflows/Tests/badge.svg)


Web Portal that provides monitoring and adminitrative tools for the RIDE Platform.

## Directory Structure

```txt
.github/                   - PR, Issue templates
app/                       - Python API Root
├── config/                - configuration exposed as environment variables
└── tests/                 - Pytest tests
frontend/                  - Frontend Root
├── src/                   - Node.js web application
│   ├── assets/            - Static File Assets
│   ├── components/        - Components Layer
│   ├── composables/       - Common composition elements
│   ├── interfaces/        - Typescript interface definitions
│   ├── lib/               - Repackaged external libraries
│   ├── router/            - Router Layer
│   ├── services/          - Services Layer
│   ├── store/             - Store Layer
│   ├── types/             - Typescript type definitions
│   ├── utils/             - Utility components
│   └── views/             - View Layer
└── tests/                 - Node.js web application tests
CODE-OF-CONDUCT.md         - Code of Conduct
COMPLIANCE.yaml            - BCGov PIA/STRA compliance status
CONTRIBUTING.md            - Contributing Guidelines
Dockerfile                 - Dockerfile Image definition
LICENSE                    - License
SECURITY.md                - Security Policy and Reporting
```

## Documentation

- [Application Readme](frontend/README.md)
- [Product Roadmap](https://github.com/bcgov/vue3-scaffold/wiki/Product-Roadmap)
- [Product Wiki](https://github.com/bcgov/vue3-scaffold/wiki)
- [Security Reporting](SECURITY.md)

## Quick Start Dev Guide

You can quickly run this application in development mode after cloning by opening two terminal windows and running the following commands (assuming you have already set up local configuration as well). Refer to the [Application Readme](app/README.md) and [Frontend Readme](app/frontend/README.md) for more details.

```
pip install -r requirements
uvicorn app.main:app --host 0.0.0.0 --port 8085
```

```
cd frontend
npm i
npm run serve
```

## Getting Help or Reporting an Issue

To report bugs/issues/features requests, please file an [issue](https://github.com/bcgov/vue3-scaffold/issues).

## How to Contribute

If you would like to contribute, please see our [contributing](CONTRIBUTING.md) guidelines.

Please note that this project is released with a [Contributor Code of Conduct](CODE-OF-CONDUCT.md). By participating in this project you agree to abide by its terms.

## License

```txt
Copyright 2022 Province of British Columbia

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
