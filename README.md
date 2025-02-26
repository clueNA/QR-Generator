![QR-Generator](https://socialify.git.ci/clueNA/QR-Generator/image?font=Source+Code+Pro&language=1&name=1&owner=1&pattern=Transparent&stargazers=1&theme=Dark)

# QR Code Generator & Reader

An interactive web application built with Streamlit that allows users to generate, read, and manage QR codes. The application features user authentication, QR code generation, reading capabilities, and a history management system.

## Features

- **User Authentication**
  - Secure login and registration system
  - Session management
  - User-specific QR code history

- **QR Code Generation**
  - Create QR codes from any text input
  - Download generated QR codes as PNG files
  - Automatic saving to user history

- **QR Code Reading**
  - Support for JPG, JPEG, and PNG formats
  - Multiple reading methods for improved accuracy
  - Option to save scanned QR codes to history

- **History Management**
  - View all generated QR codes
  - Download historical QR codes
  - Bulk deletion option
  - Clear history functionality

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/clueNA/QR-Generator
   cd QR-Generator
   ```

2. **Install system dependencies**

   For Ubuntu/Debian:
   ```bash
   sudo apt-get update
   sudo apt-get install libzbar0
   ```

   For macOS:
   ```bash
   brew install zbar
   ```

   For Windows:
   - Download and install [ZBar](https://sourceforge.net/projects/zbar/files/zbar/0.10/)

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the application**
   ```bash
   streamlit run app.py
   ```


## Dependencies

```text
streamlit
qrcode
Pillow
numpy
opencv-python
pyzbar
pytz
python-dateutil
```

## Usage

1. **Registration/Login**
   - Click on the Register button to create a new account
   - Login with your credentials
   - Your login status will be displayed in the header

2. **Generating QR Codes**
   - Navigate to the "Generate QR" tab
   - Enter your content in the text area
   - Click "Generate QR Code"
   - Download the generated QR code

3. **Reading QR Codes**
   - Go to the "Read QR" tab
   - Upload a QR code image
   - View the decoded content
   - Optionally save to history

4. **Managing History**
   - Access your QR code history in the "History" tab
   - Download previous QR codes
   - Delete individual or all QR codes

## Security Features

- Password hashing for user authentication
- Session-based user management
- Secure database operations
- Input validation and sanitization

## Database

The application uses SQLite for data storage with the following structure:
- Users table for authentication
- QR codes table for storing generated codes
- User activity logging

## Error Handling

- Image format validation
- QR code reading error recovery
- Multiple QR code reading methods
- Clear error messages and user feedback

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

- GitHub Issues: [Create Issue](https://github.com/clueNA/QR-Generator/issues)

## Acknowledgments

- Streamlit for the wonderful web framework
- QRCode library for QR code generation
- OpenCV and pyzbar for QR code reading capabilities


## Project Structure

```
qr-code-generator-reader/
├── app.py                 # Main application file
├── database.py           # Database management
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── .gitignore           # Git ignore file
```
