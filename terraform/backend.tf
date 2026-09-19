terraform {
  backend "s3" {
    bucket = "travel-booking-tfstate-v1"
    key    = "statefiles/terraform.tfstate"
    region = "eu-west-1"
  }
}
