function validateForm() {
    var fullName = document.getElementById("full_name").value;
    var email = document.getElementById("email").value;
    var phone_number = document.getElementById("phone_number").value;
    var date_of_birth = document.getElementById("dob").value;
    var password = document.getElementById("password").value;

    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        displayError("Please enter a valid email address.");
        return false;
    }

    var phoneRegex = /^\d{10}$/;
    if (!phoneRegex.test(phone_number)) {
        displayError("Please enter a valid 10-digit phone number.");
        return false;
    }

    // Check if the full name contains special characters
    if (/[^a-zA-Z\s]/.test(fullName)) {
        displayError("Special characters are not allowed in the full name.");
        return false;
    }

    if (fullName.trim() === "" || date_of_birth === "" || password === "") {
        displayError("Please fill in all the required fields.");
        return false;
    }

    // Validate date of birth
    var dob = new Date(date_of_birth);
    var currentDate = new Date();
    var minDate = new Date();
    minDate.setFullYear(currentDate.getFullYear() - 16); // Minimum date for 16 years old

    if (dob > currentDate || dob > minDate) {
        displayError("Please enter a valid date of birth. Age under 16 is not allowed and future dates are not allowed.");
        return false;
    }

    return true;
}

function displayError(message) {
    document.getElementById("error-message").textContent = message;
}
