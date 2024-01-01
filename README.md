# Whatsapp

This is a Python package that automates your WhatsApp with additional features and functionalities. This project is built to provide extended capabilities beyond the standard WhatsApp API which is paid.

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Noice75/Whatsapp2.git
    ```

2. Navigate to the project directory:

    ```bash
    cd Whatsapp2
    ```

3. Install the required dependencies:

    ```bash
    setup.py
    ```

### Usage

1. Include this package in your python file:

    ```bash
    import whatsapp
    ```

2. initialize the driver with specific preference.
   ```python
   whatsapp.Run(browser: str = 'Chrome',
            headless: bool = True,
            spawn_qr_window: bool = True,
            terminal_qr: bool = True,
            profile: str = "Default",
            wait_time: int = 0,
            command_classes: list = [],
            custom_driver: Optional[Union[ChromeWebDriver, FirefoxWebDriver]] = None,
            profile_dir: str = "Default",
            clean_start: bool = False,
            log: bool = True,
            log_to_file: bool = False,
            log_level: int = logging.CRITICAL)
   ```

3. Scan the qr to login.
4. use the api for more controll over whatsapp

### Prerequisites

- Python 3.x installed on your machine.
- Pip package manager.

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute the code for your purposes.

## Acknowledgments

- This project draws inspiration from the need for extended WhatsApp functionalities.
- This is not ment to replace whatsapp official API
---
