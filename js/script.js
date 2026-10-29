/**
 * DriveHub – Luxury Automotive Car Rental Management System
 * Theme: White & Sapphire Blue Luxury Automotive
 * Script: Core Client Interaction, Indian Phone Formatting & Demo Verification
 */

document.addEventListener('DOMContentLoaded', function () {
    // -------------------------------------------------------------
    // 1. Mobile Navigation & Interactive Menus
    // -------------------------------------------------------------
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function () {
            navLinks.classList.toggle('nav-open');
        });
    }

    // -------------------------------------------------------------
    // 2. Alert Dismissal
    // -------------------------------------------------------------
    const closeButtons = document.querySelectorAll('.alert-close');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const alert = this.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 250);
            }
        });
    });

    // -------------------------------------------------------------
    // 3. Indian Phone Number Formatting (+91)
    // -------------------------------------------------------------
    const phoneInputs = document.querySelectorAll('input[type="tel"], input[name="phone"]');
    phoneInputs.forEach(input => {
        // Enforce starting with +91 if empty on focus
        input.addEventListener('focus', function () {
            if (!this.value.trim()) {
                this.value = '+91 ';
            }
        });

        input.addEventListener('input', function () {
            let val = this.value;
            // Ensure +91 prefix
            if (!val.startsWith('+91')) {
                // If user typed digits only, re-attach +91
                let digits = val.replace(/\D/g, '');
                if (digits.startsWith('91')) {
                    digits = digits.slice(2);
                }
                this.value = '+91 ' + digits.slice(0, 10);
            } else {
                let rest = val.slice(3).replace(/\D/g, '');
                this.value = '+91 ' + rest.slice(0, 10);
            }
        });
    });

    // -------------------------------------------------------------
    // 4. Demo Licence Verification: Dynamic RTO State Preview
    // -------------------------------------------------------------
    const rtoStateMap = {
        'AN': 'Andaman & Nicobar',
        'AP': 'Andhra Pradesh',
        'AR': 'Arunachal Pradesh',
        'AS': 'Assam',
        'BR': 'Bihar',
        'CH': 'Chandigarh',
        'CG': 'Chhattisgarh',
        'DL': 'Delhi',
        'DN': 'Dadra & Nagar Haveli',
        'DD': 'Daman & Diu',
        'GA': 'Goa',
        'GJ': 'Gujarat',
        'HR': 'Haryana',
        'HP': 'Himachal Pradesh',
        'JK': 'Jammu & Kashmir',
        'JH': 'Jharkhand',
        'KA': 'Karnataka',
        'KL': 'Kerala',
        'LA': 'Ladakh',
        'LD': 'Lakshadweep',
        'MP': 'Madhya Pradesh',
        'MH': 'Maharashtra',
        'MN': 'Manipur',
        'ML': 'Meghalaya',
        'MZ': 'Mizoram',
        'NL': 'Nagaland',
        'OD': 'Odisha',
        'PB': 'Punjab',
        'PY': 'Puducherry',
        'RJ': 'Rajasthan',
        'SK': 'Sikkim',
        'TN': 'Tamil Nadu',
        'TS': 'Telangana',
        'TR': 'Tripura',
        'UP': 'Uttar Pradesh',
        'UK': 'Uttarakhand',
        'UA': 'Uttarakhand',
        'WB': 'West Bengal'
    };

    const dlInput = document.querySelector('#licence_number_input');
    const rtoBadge = document.querySelector('#rto_state_badge');

    if (dlInput && rtoBadge) {
        dlInput.addEventListener('input', function () {
            const raw = this.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
            if (raw.length >= 2) {
                const code = raw.slice(0, 2);
                if (rtoStateMap[code]) {
                    rtoBadge.textContent = 'Detected RTO: ' + rtoStateMap[code] + ' (' + code + ')';
                    rtoBadge.className = 'badge badge-approved fs-xs mt-05 d-inline-flex';
                } else {
                    rtoBadge.textContent = 'Unrecognized Indian State Code: ' + code;
                    rtoBadge.className = 'badge badge-warning fs-xs mt-05 d-inline-flex';
                }
            } else {
                rtoBadge.textContent = 'Enter Indian DL Number (e.g., DL-04-2023-XXXXXXX)';
                rtoBadge.className = 'badge badge-normal fs-xs mt-05 d-inline-flex';
            }
        });
    }

    // -------------------------------------------------------------
    // 5. Booking Price Calculation in Indian Rupees (₹)
    // -------------------------------------------------------------
    const startDateInput = document.querySelector('#booking_start_date');
    const endDateInput = document.querySelector('#booking_end_date');
    const dailyRateElem = document.querySelector('#car_daily_rate');
    const depositElem = document.querySelector('#car_deposit_amount');
    const daysCalcElem = document.querySelector('#calc_days');
    const rentalChargeCalcElem = document.querySelector('#calc_rental_charge');
    const totalAmountCalcElem = document.querySelector('#calc_total_amount');

    function updateBookingSummary() {
        if (!startDateInput || !endDateInput || !dailyRateElem) return;

        const startVal = startDateInput.value;
        const endVal = endDateInput.value;
        if (!startVal || !endVal) return;

        const dStart = new Date(startVal);
        const dEnd = new Date(endVal);

        if (dEnd > dStart) {
            const diffTime = Math.abs(dEnd - dStart);
            const totalDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            const dailyRate = parseFloat(dailyRateElem.getAttribute('data-rate') || 0);
            const deposit = parseFloat(depositElem ? depositElem.getAttribute('data-deposit') || 0 : 0);

            const rentalCharge = totalDays * dailyRate;
            const grandTotal = rentalCharge + deposit;

            if (daysCalcElem) daysCalcElem.textContent = totalDays + (totalDays === 1 ? ' Day' : ' Days');
            if (rentalChargeCalcElem) rentalChargeCalcElem.textContent = '₹' + rentalCharge.toLocaleString('en-IN');
            if (totalAmountCalcElem) totalAmountCalcElem.textContent = '₹' + grandTotal.toLocaleString('en-IN');
        }
    }

    if (startDateInput && endDateInput) {
        startDateInput.addEventListener('change', updateBookingSummary);
        endDateInput.addEventListener('change', updateBookingSummary);
        updateBookingSummary();
    }
});
