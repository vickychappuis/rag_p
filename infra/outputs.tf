output "qdrant_public_ip" {
  value = aws_instance.qdrant.public_ip
}

output "qdrant_private_ip" {
  value = aws_instance.qdrant.private_ip
}

output "backend_public_ip" {
  value = aws_instance.backend.public_ip
}

output "api_gateway_url" {
  value = aws_apigatewayv2_stage.default.invoke_url
}

output "playground_url" {
  value = "${aws_apigatewayv2_stage.default.invoke_url}/chat/playground"
}

output "ssh_qdrant" {
  value = "ssh -i infra/promtior-deployer.pem ubuntu@${aws_instance.qdrant.public_ip}"
}

output "ssh_backend" {
  value = "ssh -i infra/promtior-deployer.pem ubuntu@${aws_instance.backend.public_ip}"
}
