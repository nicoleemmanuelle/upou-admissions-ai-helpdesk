output "ec2_ip" {
  value = aws_instance.web.public_ip
}