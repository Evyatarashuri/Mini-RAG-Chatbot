import React from "react";

const GoogleLoginButton = () => {
  const handleClick = () => {
    alert("Google Login flow will go here!");
  };

  return (
    <button className="google-btn" onClick={handleClick}>
      <img src="https://developers.google.com/identity/images/g-logo.png" alt="Google" />
      Continue with Google
    </button>
  );
};

export default GoogleLoginButton;
