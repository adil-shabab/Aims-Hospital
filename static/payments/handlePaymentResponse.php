<?php
use PaymentHandler\PaymentHandler;
require_once realpath("./PaymentHandler.php");

$paymentHandler = new PaymentHandler("config.json");
$response = $_POST;

try {
    if ($paymentHandler->validateHMAC_SHA256($response)) {
        // If validation is successful, extract the necessary details from the response
        $appointmentId = $response['appointment_id'];  // Extract the appointment ID
        $amount = $response['amount'];  // Extract the amount from the response
        $order_id = $response['order_id'];

        // Define the base URL for the Django server
        $updateUrl = "https://vshhospital.com/update-appointment-status";

        // Prepare the query parameters
        $params = http_build_query([
            'amount' => $amount,
            'appointment_id' => $appointmentId,
            'order_id' => $order_id,
        ]);


        // Redirect to the URL with the query parameters
        header("Location: {$updateUrl}?{$params}");
        exit;
        
    } else {
        // Payment verification failed
        $appointmentId = $response['appointment_id'];  // Extract the appointment ID
        $amount = $response['amount'];  // Extract the amount from the response
        $order_id = $response['order_id'];

        // Define the base URL for the Django server
        $updateUrl = "https://vshhospital.com/update-appointment-status";

        // Prepare the query parameters
        $params = http_build_query([
            'amount' => $amount,
            'appointment_id' => $appointmentId,
            'order_id' => $order_id,
        ]);


        // Redirect to the URL with the query parameters
        header("Location: {$updateUrl}?{$params}");
        exit;
    }
} catch (Exception $e) {
    // Handle any errors that occur during payment verification
    echo "Error handling payment: " . $e->getMessage();
}
?>
