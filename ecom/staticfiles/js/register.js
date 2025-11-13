// Indicateur de force du mot de passe
    if (password) {
      password.addEventListener('input', function() {
        const value = this.value;
        let strength = 0;

        if (value.length >= 8) strength++;
        if (value.match(/[a-z]/) && value.match(/[A-Z]/)) strength++;
        if (value.match(/[0-9]/)) strength++;
        if (value.match(/[^a-zA-Z0-9]/)) strength++;

        strengthBar.className = 'password-strength-bar';
        if (strength <= 1) {
          strengthBar.classList.add('weak');
        } else if (strength <= 3) {
          strengthBar.classList.add('medium');
        } else {
          strengthBar.classList.add('strong');
        }
      });
    }

