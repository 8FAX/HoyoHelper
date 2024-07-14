# Hoyo Helper Project

## Overview
The Hoyo Helper project is an ambitious endeavor aimed at creating a seamless application that integrates various functionalities to enhance user experience. At its core, the project leverages the power of automation, GUI development, and backend scripting to provide a comprehensive solution. Currently, the project components are being developed separately to allow for focused development and easier integration in the future.

### Components

#### Playwright Automation for Auto-Login
The project utilizes Playwright, a powerful automation library, to automate the login process for websites. This component is responsible for navigating to the login page, entering credentials, and managing session cookies post-login. The automation script is designed to run asynchronously, ensuring a smooth and efficient login process. The script is located in the file.

#### Client GUI
The Client GUI is developed to provide an intuitive and user-friendly interface for interacting with the application. It includes various UI elements for triggering actions such as login, settings configuration, and more. The GUI is split into two main scripts for the main application window and for a windowless variant, offering flexibility in how the application is presented to the user.

#### Backend Login Script
The backend login script, serves as the backbone for handling authentication. It is designed to work in tandem with the Playwright automation to manage user credentials and session information securely.

### Future Integration
The ultimate goal of the Hoyo Helper project is to integrate these separate components into one seamless application. This integration will allow for a cohesive user experience, where the GUI provides a friendly interface for the automation and backend scripts to operate efficiently in the background. The modular development approach currently employed facilitates easier updates and maintenance, setting a solid foundation for the final integrated application.

### Development Status
As of now, the project components are under active development. Each component is being refined to ensure reliability and efficiency. Future updates will focus on integrating these components, enhancing the GUI, and expanding the automation capabilities to cover more use cases.

### Contributions
Contributions to the Hoyo Helper project are welcome. Whether it's improving the existing code, suggesting new features, or reporting bugs, your input is valuable in making this project a success.

### License
This project (all files / assets / other in all branches) is licensed under the GNU Affero General Public License wether or not they have a notice in the header. - see the [LICENSE](https://github.com/8FAX/HoyoHelper/blob/main/LICENSE.md) file for details .

---

This README provides a brief overview of the Hoyo Helper project. For more detailed information on each component, please refer to the respective script documentation. (not made yet )