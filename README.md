# Declaro

Robot to automate the process of tax declaration in the Mexican IRS (SAT) for independet professionals (Personas físicas con actividad empresarial)

## Getting Started

You need to mount in Mongo Atlas a Data base named "api" with the following collections:
- usuarios
- facturas

Adapt Mongo's string for the conection and also create a file named "pw.txt" where you save your password of Mongo Altas in the first line of the file.

### Prerequisites

Needed libraries:

- pymongo
- selenium

You need to install

```
pip3 install pymongo
pip3 install selenium
```

## Running the tests

You can run every module separatly to check that is working (Modules 3 to 7) but first you need to run modules 1 and 2 regarding the libraries and the functions

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
