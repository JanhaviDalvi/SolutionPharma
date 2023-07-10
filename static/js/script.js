// to set time for flashed messages in 'layout.html'
var flash_div = document.getElementById("flash_div");
if (flash_div) {
	setTimeout(function () {
		flash_div.style.display = "none";
	}, 8000); // Hide the div after 8 seconds
}

function calculateTotalCost() {
    var total = 0;
    var totalCostElements = document.querySelectorAll('#medicine-table-body td:nth-child(4)');
    var total_hidden = document.getElementById("total_amount");

    totalCostElements.forEach(function (element) {
        var cost = parseFloat(element.textContent);
        if (!isNaN(cost)) {
            total += cost;
        }
    });

    var totalCostElement = document.getElementById('total-cost');
    totalCostElement.textContent = total.toFixed(2);
    total_hidden.setAttribute("value", totalCostElement.textContent);
}

function addMedicine() {
    console.log("add pressed!")
    // Get the selected medicine name and quantity
    var name_price = document.getElementById('productName').value;
    name_price = name_price.split(',');
    var medicine_name = name_price[0];
    var medicine_price = parseFloat(name_price[1]);
    var quantity = parseFloat(document.getElementById('productQuantity').value);

    // Calculate the total cost
    var totalCost = quantity * medicine_price;
    // Create a new table row
    var row = document.createElement('tr');
    // Add the medicine name, quantity, price, and total cost to the table row
    row.innerHTML = `
        <td name='medicine_name'>${medicine_name}</td>
        <td name='medicine_quantity'>${quantity}</td>
        <td name='medicine_price'>${medicine_price}</td>
        <td name='medicine_totalCost'>${totalCost}</td>
        <td>
            <input type="hidden" name="medicine_name[]" value="${medicine_name}">
            <input type="hidden" name="medicine_quantity[]" value="${quantity}">
            <input type="hidden" name="medicine_price[]" value="${medicine_price}">
            <input type="hidden" name="medicine_totalCost[]" value="${totalCost}">
            <button class="btn btn-danger btn-sm delete-btn">Delete</button>
        </td>
    `;
    // Append the new row to the table body
    document.getElementById('medicine-table-body').appendChild(row);

    // Attach a click event listener to the delete button
    var deleteButton = row.querySelector('.delete-btn');
    deleteButton.addEventListener('click', function() {
        // Find the closest <tr> element (row) and remove it
        var row = this.closest('tr');
        row.remove();
        calculateTotalCost();
    });
    calculateTotalCost();
}

// for 'billing.html'
function printReceipt() {
    var printContents = document.getElementById("billing-receipt").innerHTML;
    var originalContents = document.body.innerHTML;

    document.body.innerHTML = printContents;
    window.print();
    document.body.innerHTML = originalContents;
}

// for 'sales_report.html'
document.getElementById('reportType').addEventListener('change', function() {
    var selectedOption = this.value;

    var dateInput = document.getElementById('dateInput');
    var companyInput = document.getElementById('companyInput');

    if (selectedOption === 'billing_date') {
        dateInput.style.display = 'block';
        companyInput.style.display = 'none';
    } else if (selectedOption === 'mdcn_company') {
        dateInput.style.display = 'none';
        companyInput.style.display = 'block';
    }
});