provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "web_server" {
  ami = "ami-0f1a6835595fb9246"
  instance_type = "t2.medium"
  availability_zone = "us-east-1a"
  subnet_id = aws_subnet.public[0].id  
  tags = {
    Name = "WebServer"
  }
}
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  enable_dns_support = true
  enable_dns_hostnames = true
  tags = {
    Name = "Or Main VPC"
  }
}
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags={
      Name = "Or Main Internet Gateway"
  }
}
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "Public Route Table"
  }
}

resource "aws_route_table_association" "public_association" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}


resource "aws_subnet" "public" {
  count = 2
  vpc_id = aws_vpc.main.id
  map_public_ip_on_launch = true
  cidr_block = "10.0.${count.index}.0/24"
  availability_zone = element(["us-east-1a", "us-east-1b"], count.index)
    tags = {
    Name = "Public Subnet for or ${count.index + 1}"
  }
}

resource "aws_security_group" "lb_sg" {
  name        = "lb_security_group_or"
  description = "Allow HTTP inbound traffic"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

   
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "LoadBalancerSG"
  }
}
resource "aws_lb" "application_lb" {
  name = "orload"
  internal = false
  load_balancer_type = "application"
  security_groups = [aws_security_group.lb_sg.id]
  subnets = aws_subnet.public[*].id

 
  tags = {
    Name = "application-lb"
  }
}

resource "aws_lb_listener" "http_listener" {
  load_balancer_arn = aws_lb.application_lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web_target_group.arn
  }
}

resource "aws_lb_target_group" "web_target_group" {
  name     = "web-target-group-or"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
}

resource "aws_lb_target_group_attachment" "web_instance_attachment" {
  target_group_arn = aws_lb_target_group.web_target_group.arn
  target_id        = aws_instance.web_server.id
}



# resource "aws_vpc" "main" {
#   cidr_block = "10.0.0.0/16"
# }



output "web_server_instance_id" {
  value = aws_instance.web_server.id
}

output "load_balancer_dns" {
  value = aws_lb.application_lb.dns_name
}