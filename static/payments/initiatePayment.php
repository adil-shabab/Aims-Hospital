<?php

// Import PaymentHandler class
use PaymentHandler\PaymentHandler;
require_once realpath("./PaymentHandler.php");

// Check if 'appointment_id' and 'amount' are passed as parameters
if (!isset($_GET['appointment_id']) || !isset($_GET['amount'])) {
    http_response_code(400);
    echo json_encode(["error" => "Missing appointment_id or amount"]);
    exit;
}

// Extract and validate appointment ID and amount
$appointmentId = $_GET['appointment_id'];
$amount = intval($_GET['amount']);  // Ensure amount is an integer (in paise)

// Generate a unique order ID
$orderId = "order_" . uniqid();

// Dynamic customer ID (replace this with actual logic)
$customerId = "customer_" . uniqid();

try {
    // Load the payment handler configuration from config.json
    $paymentHandler = new PaymentHandler("config.json");

    // Create a new payment session by calling the HDFC API
    $session = $paymentHandler->orderSession([
        "amount" => $amount / 100,  // Amount in paise (passed dynamically)
        "order_id" => $orderId,
        "appointment_id" => $appointmentId,
        "customer_id" => $customerId,  // Replace this with actual customer logic
        "action" => "paymentPage",
        "return_url" => "https://vshhospital.com/static/payments/handlePaymentResponse.php?appointment_id=$appointmentId&amount=$amount"  // HDFC will redirect to this URL after payment
    ]);

    // Redirect the user to the HDFC payment page
    header("Location: {$session['payment_links']['web']}");
    exit;

} catch (Exception $e) {
    // Log the error for debugging purposes
    error_log("Error initiating payment: " . $e->getMessage(), 3, '/var/log/php_errors.log');

    // Handle any errors that occur during payment session creation
    http_response_code(500);
    echo json_encode(["error" => "Error initiating payment: " . $e->getMessage()]);
}
?>
