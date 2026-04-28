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
  value = "https://rag.vickychappuis.dev/chat/playground"
}

output "acm_validation_cname_name" {
  value       = tolist(aws_acm_certificate.rag.domain_validation_options)[0].resource_record_name
  description = "Namecheap: CNAME Host (validacion ACM)"
}

output "acm_validation_cname_value" {
  value       = tolist(aws_acm_certificate.rag.domain_validation_options)[0].resource_record_value
  description = "Namecheap: CNAME Value (validacion ACM)"
}

output "rag_domain_cname_value" {
  value       = aws_apigatewayv2_domain_name.rag.domain_name_configuration[0].target_domain_name
  description = "Namecheap: CNAME Value para rag.vickychappuis.dev"
}

output "ssh_qdrant" {
  value = "ssh -i infra/promtior-deployer.pem ubuntu@${aws_instance.qdrant.public_ip}"
}

output "ssh_backend" {
  value = "ssh -i infra/promtior-deployer.pem ubuntu@${aws_instance.backend.public_ip}"
}
