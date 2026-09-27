<script lang="ts">
  import { goto } from "$app/navigation";
  import { cart, clearCart, removeFromCart, setQuantity } from "$lib/cart";

  let shippingAddress = "";
  let checkingOut = false;
  let error = "";

  $: total = $cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  async function checkout() {
    error = "";
    if (!$cart.length) return;
    if (shippingAddress.trim().length < 3) {
      error = "Enter a shipping address.";
      return;
    }

    checkingOut = true;
    try {
      const response = await fetch("http://localhost:8000/api/orders/checkout", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          shipping_address: shippingAddress.trim(),
          items: $cart.map((item) => ({
            product_id: item.id,
            quantity: item.quantity,
          })),
        }),
      });
      const data = await response.json();

      if (!response.ok) {
        error = response.status === 401 ? "Log in before checking out." : data.detail ?? "Checkout failed.";
        return;
      }

      clearCart();
      goto(`/orders/${data.id}`);
    } catch {
      error = "Could not reach the checkout service.";
    } finally {
      checkingOut = false;
    }
  }
</script>

<header class="page-heading">
  <div>
    <p class="eyebrow">SHOPPING CART</p>
    <h1>My Cart</h1>
  </div>
  {#if $cart.length}
    <button class="text-button" on:click={clearCart}>Clear cart</button>
  {/if}
</header>

{#if !$cart.length}
  <section class="empty-state">
    <h2>Your cart is empty</h2>
    <p class="muted">Browse the catalog and add something to get started.</p>
    <a class="button" href="/products">Browse products</a>
  </section>
{:else}
  <div class="cart-layout">
    <section class="cart-items" aria-label="Cart items">
      {#each $cart as item (item.id)}
        <article class="cart-row">
          <div class="cart-product-mark">CC</div>
          <div class="cart-product-copy">
            <a href={`/product/${item.id}`}><strong>{item.name}</strong></a>
            <span class="muted">₹{item.price} each</span>
          </div>
          <div class="quantity-control" aria-label={`Quantity for ${item.name}`}>
            <button aria-label={`Decrease ${item.name} quantity`} on:click={() => setQuantity(item.id, item.quantity - 1)}>−</button>
            <input
              aria-label={`${item.name} quantity`}
              type="number"
              min="1"
              max="99"
              value={item.quantity}
              on:change={(event) => setQuantity(item.id, Number(event.currentTarget.value))}
            />
            <button aria-label={`Increase ${item.name} quantity`} on:click={() => setQuantity(item.id, item.quantity + 1)}>+</button>
          </div>
          <strong class="line-total">₹{item.price * item.quantity}</strong>
          <button class="remove-button" aria-label={`Remove ${item.name}`} on:click={() => removeFromCart(item.id)}>Remove</button>
        </article>
      {/each}
    </section>

    <aside class="checkout-panel">
      <h2>Order summary</h2>
      <div class="summary-line">
        <span>Subtotal</span>
        <strong>₹{total}</strong>
      </div>
      <div class="summary-line">
        <span>Shipping</span>
        <strong>Free</strong>
      </div>
      <div class="summary-line total-line">
        <span>Total</span>
        <strong>₹{total}</strong>
      </div>

      <label for="shipping-address">
        Shipping address
        <textarea id="shipping-address" bind:value={shippingAddress} rows="3" maxlength="255" placeholder="10 Example Street"></textarea>
      </label>

      {#if error}
        <div class="notice error-notice">{error}</div>
        {#if error.includes("Log in")}
          <a class="login-link" href="/login">Go to login</a>
        {/if}
      {/if}

      <button class="button checkout-button" on:click={checkout} disabled={checkingOut}>
        {checkingOut ? "Placing order..." : "Checkout"}
      </button>
    </aside>
  </div>
{/if}
