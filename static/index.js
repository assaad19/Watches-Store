function addToCart(productId) {
  // Send a POST request to add the product to the cart
  fetch("/add_to_cart/" + productId, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ product_id: productId }),
  })
    .then((response) => {
      if (response.ok) {
        // Increment the cart count in the span element
        let cartCountElement = document.getElementById("cart-count");
        let currentCount = parseInt(cartCountElement.innerText);
        cartCountElement.innerText = currentCount + 1;
      } else {
        console.error("Failed to add product to cart");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
  console.log("Adding product with ID:", productId);
}

function checkout() {
  // Alert the user about the successful purchase
  alert("Your purchase was successful");

  // Empty the cart by redirecting to a route that handles cart emptying
  window.location.href = "/user"; // Replace 'empty_cart' with the appropriate route
}
