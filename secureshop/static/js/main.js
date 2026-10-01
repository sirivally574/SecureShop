// SecureShop Frontend JavaScript Helper
document.addEventListener("DOMContentLoaded", function () {
  // 1. Auto-dismiss alerts after 5 seconds
  const flashAlerts = document.querySelectorAll(".flash-message");
  flashAlerts.forEach(function (alert) {
    setTimeout(function () {
      alert.style.opacity = "0";
      alert.style.transition = "opacity 0.5s ease";
      setTimeout(function () {
        alert.remove();
      }, 500);
    }, 5000);
  });

  // 2. Clipboard copy for safe test payloads
  window.copyToClipboard = function (text, btnElement) {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(onSuccess, onFallback);
    } else {
      onFallback();
    }

    function onSuccess() {
      if (btnElement) {
        const originalText = btnElement.innerText;
        btnElement.innerText = "Copied!";
        btnElement.style.background = "#10B981";
        setTimeout(() => {
          btnElement.innerText = originalText;
          btnElement.style.background = "";
        }, 2000);
      }
    }

    function onFallback() {
      const textArea = document.createElement("textarea");
      textArea.value = text;
      textArea.style.position = "fixed";
      textArea.style.left = "-9999px";
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      try {
        document.execCommand("copy");
        onSuccess();
      } catch (err) {
        console.error("Failed to copy", err);
      }
      document.body.removeChild(textArea);
    }
  };

  // 3. Confirm Delete Actions
  const deleteButtons = document.querySelectorAll("[data-confirm]");
  deleteButtons.forEach(function (button) {
    button.addEventListener("click", function (e) {
      const msg = this.getAttribute("data-confirm") || "Are you sure you want to proceed?";
      if (!confirm(msg)) {
        e.preventDefault();
      }
    });
  });
});
