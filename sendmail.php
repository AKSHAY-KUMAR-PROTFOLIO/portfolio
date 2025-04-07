
<?php
    
    {
        $name = $_POST["name"];
        $email = $_POST["email"];
        $description = $_POST["description"];


        $to = "akmodsyt@gmail.com";
        $subject = "New Contact Form Submission";
        $body = "Name: {$name}\nEmail: {$email}\nMessage: {$description}";
        $headers = "From: {$email}";


        if (mail($to, $subject, $body, $headers)) {
            echo "Message sent successfully!";
        } else {
            echo "Failed to send message.";
        }
    }
?>
