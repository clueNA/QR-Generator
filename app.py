import streamlit as st
import qrcode
from io import BytesIO
from database import DatabaseManager
import base64
import logging
from datetime import datetime
import pytz
from PIL import Image
import numpy as np
import cv2

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
db = DatabaseManager()

# Configure page settings
st.set_page_config(
    page_title="QR Code Generator & Reader",
    page_icon="🔲",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_user_info():
    """Get formatted user info with UTC time"""
    current_time = datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
    username = st.session_state.get('username', 'Not logged in')
    return (f"Current Date and Time: {current_time}\n"
            f"Current User's Login: {username}")

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

def read_qr_code(image_data):
    try:
        image = Image.open(image_data)
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert PIL Image to OpenCV format
        image_np = np.array(image)
        # OpenCV uses BGR but PIL uses RGB, so convert
        image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        
        # Initialize QR Code detector
        qr_detector = cv2.QRCodeDetector()
        
        # Try to detect and decode QR code
        data, bbox, _ = qr_detector.detectAndDecode(image_cv)
        
        if data:
            # Successfully detected QR code
            return [data]
        
        # If standard detection fails, try with preprocessing
        gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
        
        # Try with threshold
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 11, 2)
        data, bbox, _ = qr_detector.detectAndDecode(thresh)
        
        if data:
            return [data]
        
        # Try with blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        data, bbox, _ = qr_detector.detectAndDecode(thresh)
        
        if data:
            return [data]
            
        # If we get here, no QR code was detected
        return None
    except Exception as e:
        logger.error(f"Error reading QR code: {e}")
        return None

def delete_data_with_confirmation():
    """Handle the deletion confirmation process"""
    if 'delete_stage' not in st.session_state:
        st.session_state.delete_stage = 'initial'

    if st.session_state.delete_stage == 'initial':
        if st.button("🗑️ Delete All My QR Codes"):
            st.session_state.delete_stage = 'confirming'
            st.rerun()

    elif st.session_state.delete_stage == 'confirming':
        st.warning("⚠️ Are you sure you want to delete all your QR codes? This action cannot be undone!")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Yes, Delete All Data"):
                deleted_count = db.delete_user_data(st.session_state.user_id)
                if deleted_count > 0:
                    st.success(f"Successfully deleted {deleted_count} QR codes!")
                else:
                    st.info("No QR codes to delete.")
                st.session_state.delete_stage = 'initial'
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.delete_stage = 'initial'
                st.rerun()

def main():
    # Session state initialization
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

    # Display user info at the top of the page
    st.markdown(f"```\n{get_user_info()}\n```")
    
    # Display title
    st.title("QR Code Generator & Reader")

    # Sidebar
    with st.sidebar:
        st.title("Authentication")
        if st.session_state.user_id is None:
            tab1, tab2 = st.tabs(["Login", "Register"])
            
            with tab1:
                st.header("Login")
                login_username = st.text_input("Username", key="login_username")
                login_password = st.text_input("Password", type="password", key="login_password")
                if st.button("Login"):
                    user_id = db.verify_user(login_username, login_password)
                    if user_id:
                        st.session_state.user_id = user_id
                        st.session_state.username = login_username
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
            
            with tab2:
                st.header("Register")
                reg_username = st.text_input("Username", key="reg_username")
                reg_password = st.text_input("Password", type="password", key="reg_password")
                if st.button("Register"):
                    if db.create_user(reg_username, reg_password):
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Username already exists")
        else:
            st.success(f"Logged in as: {st.session_state.username}")
            if st.button("Logout"):
                st.session_state.clear()
                st.rerun()

            # Data Management Section
            st.markdown("---")
            st.header("Data Management")
            
            # Show QR code count
            qr_count = db.get_user_qr_code_count(st.session_state.user_id)
            st.info(f"Total QR Codes: {qr_count}")
            
            # Delete data section
            st.markdown("### Delete Data")
            delete_data_with_confirmation()

    # Main content area
    if st.session_state.user_id is not None:
        tabs = st.tabs(["Generate QR", "Read QR", "History"])
        
        # Generate QR tab
        with tabs[0]:
            col1, col2 = st.columns(2)
            
            with col1:
                st.header("Generate QR Code")
                qr_content = st.text_area("Enter content for QR code", height=150)
                
                if st.button("Generate QR Code"):
                    if qr_content:
                        if db.save_qr_code(st.session_state.user_id, qr_content):
                            st.success("QR code generated and saved!")
                        else:
                            st.error("Failed to save QR code")
                    else:
                        st.warning("Please enter content")

            with col2:
                st.header("QR Code Display")
                if qr_content:
                    qr_image = generate_qr_code(qr_content)
                    st.image(qr_image, caption="Generated QR Code")
                    st.download_button(
                        label="Download QR Code",
                        data=qr_image,
                        file_name="qr_code.png",
                        mime="image/png"
                    )

        # Read QR tab
        with tabs[1]:
            st.header("Read QR Code")
            st.info("Supported formats: JPG, JPEG, PNG")
            
            uploaded_file = st.file_uploader(
                "Choose a QR code image",
                type=['jpg', 'jpeg', 'png']
            )
            
            if uploaded_file:
                st.image(uploaded_file, caption="Uploaded Image", width=300)
                
                with st.spinner("Reading QR code..."):
                    qr_contents = read_qr_code(uploaded_file)
                
                if qr_contents:
                    st.success("QR Code(s) Read Successfully!")
                    for i, content in enumerate(qr_contents, 1):
                        st.markdown(f"**QR Code {i} Content:**")
                        st.code(content)
                        
                        if st.button(f"Save QR Code {i} to History"):
                            if db.save_qr_code(st.session_state.user_id, content):
                                st.success("Saved to history!")
                            else:
                                st.error("Failed to save")
                else:
                    st.error("No QR code found in the image")
                    st.markdown("""
                    **Troubleshooting Tips:**
                    - Ensure the QR code is clearly visible
                    - Check if the image is well-lit and focused
                    - Try a different image format
                    - Make sure the QR code has good contrast
                    """)

        # History tab
        with tabs[2]:
            st.header("Your QR Code History")
            history = db.get_user_qr_codes(st.session_state.user_id)
            
            if not history:
                st.info("No QR codes in history")
            else:
                for content, created_at in history:
                    with st.expander(f"QR Code - {created_at}"):
                        st.write("Content:", content)
                        qr_image = generate_qr_code(content)
                        st.image(qr_image, width=200)
                        st.download_button(
                            label="Download",
                            data=qr_image,
                            file_name=f"qr_code_{created_at}.png",
                            mime="image/png",
                            key=f"download_{created_at}"
                        )

    else:
        st.info("Please login or register to use the QR code generator")

if __name__ == "__main__":
    main()
