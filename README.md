Project Overview and Bugs
1. main.py
user_input:
This part collects all the required input from the user.
The AMI changes depending on the OS, using a suitable AMI that I found online.

terraform_setup:
This section uses a Jinja2 template to render the Terraform configuration into the main.tf file.
It reads from terraform_template.j2 and saves the output in main.tf.

run_myterraform:
This function runs all the Terraform commands and extracts the EC2 instance ID and Load Balancer DNS.
Major bug: The code always fails at terraform plan. Due to time constraints, I couldn't find a solution.
This bug affects the rest of the script because I don't have JSON input. However, I wrote the code for this part and all other sections in the exam.
Note: If I run terraform apply and terraform plan from the terminal manually, everything works as expected. The issue occurs when running the Python script.

aws_part:
This function uses boto3 to check if the EC2 instance and Load Balancer are running. If they are not, it starts them.
It also saves the requested IP, DNS, and states inside a JSON file.
Unfortunately, as mentioned earlier, I wrote the code, but I didn't have enough time to fix the bug that also affects this function.

2. terraform_template.j2
I made several changes from the base code:
Added aws_vpc.main to support DNS resolution and hostnames.
Added an Internet Gateway, as Terraform apply was failing due to its absence.
Added aws_route_table and aws_route_table_association to connect all subnets and gateways to the internet.
In aws_instance.web_server, I changed the subnet ID to ensure it can get a public IP for the Load Balancer.

In aws_security_group.lb_sg:
Changed ingress port to 443 (TCP) to navigate traffic.
This change also helped fix a security group bug I encountered.
Added outbound rules (egress) to allow the Load Balancer to communicate with different destinations on the web.
Changed some names and tags in the code.
Finally, I added two new Terraform outputs:
web_server_instance_id
load_balancer_dns
However, I'm not sure if these additions really helped.
