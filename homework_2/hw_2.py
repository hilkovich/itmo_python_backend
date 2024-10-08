import uvicorn
from http import HTTPStatus
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Response

from models import Cart, Item, ItemCart, ItemAdd

app = FastAPI(title="Shop API")

items = []
carts = []


# POST
@app.post("/cart", status_code=HTTPStatus.CREATED)
def create_cart(response: Response):
    id = len(carts) + 1
    cart = Cart(id=id)
    carts.append(cart)
    response.headers["location"] = f"/cart/{cart.id}"
    return cart


@app.post("/item", status_code=HTTPStatus.CREATED)
def create_item(item: ItemAdd, response: Response):
    id = len(items) + 1
    item = Item(id=id, name=item.name, price=item.price, deleted=False)
    items.append(item)
    response.headers["location"] = f"/item/{item.id}"
    return item


@app.post("/cart/{cart_id}/add/{item_id}", response_model=Cart)
def add_item_cart(cart_id: int, item_id: int):
    for cart in carts:
        if cart.id == cart_id:
            for item in items:
                if item.id == item_id and not item.deleted:
                    for current_item in cart.items:
                        if current_item.id == item_id:
                            current_item.quantity += 1
                            cart.price += item.price
                            return cart
                    cart.items.append(
                        ItemCart(id=item.id, name=item.name, quantity=1, available=True)
                    )
                    cart.price += item.price
                    return cart
            raise HTTPException(
                detail="Item not found",
                status_code=HTTPStatus.NOT_FOUND,
            )
    raise HTTPException(
        detail="Cart not found",
        status_code=HTTPStatus.NOT_FOUND,
    )


# GET
@app.get("/cart/{id}", response_model=Cart)
def get_cart(id: int):
    for cart in carts:
        if cart.id == id:
            return cart
    raise HTTPException(detail="Cart not found", status_code=HTTPStatus.NOT_FOUND)


@app.get("/item/{id}", response_model=Item)
def get_item(id: int):
    for item in items:
        if item.id == id and not item.deleted:
            return item
    raise HTTPException(detail="Item not found", status_code=HTTPStatus.NOT_FOUND)


@app.get("/cart", response_model=List[Cart])
def list_cart(
    offset: int = 0,
    limit: int = 10,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_quantity: Optional[int] = None,
    max_quantity: Optional[int] = None,
):
    filter_carts = []
    if offset < 0:
        raise HTTPException(
            detail="Offset must be positive",
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        )
    if limit <= 0:
        raise HTTPException(
            detail="Limit must be greater than 0",
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        )
    if (min_price is not None) and min_price < 0:
        raise HTTPException(
            detail="min_price must be greater than 0",
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        )
    if (max_price is not None) and max_price < 0:
        raise HTTPException(
            detail="max_price must be greater than 0",
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        )
    if (min_quantity is not None) and min_quantity < 0:
        raise HTTPException(
            detail="min_quantity must be greater than 0",
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        )
    if (max_quantity is not None) and max_quantity < 0:
        raise HTTPException(
            detail="max_quantity must be greater than 0",
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        )

    for i in range(offset, len(carts)):
        if len(filter_carts) == limit:
            break
        cart = carts[i]
        if (
            (min_price is None or cart.price >= min_price)
            and (max_price is None or cart.price <= max_price)
            and (
                min_quantity is None
                or sum(item.quantity for item in cart.items) >= min_quantity
            )
            and (
                max_quantity is None
                or sum(item.quantity for item in cart.items) <= max_quantity
            )
        ):
            filter_carts.append(cart)

    return filter_carts


@app.get("/item", response_model=List[Item])
def list_items(
    offset: int = 0,
    limit: int = 10,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    show_deleted: bool = False,
):
    filter_items = []
    if offset < 0:
        raise HTTPException(
            detail="Offset must be positive",
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        )
    if limit <= 0:
        raise HTTPException(
            detail="Limit must be greater than 0",
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        )
    if (min_price is not None) and min_price < 0:
        raise HTTPException(
            detail="min_price must be greater than 0",
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        )
    if (max_price is not None) and max_price < 0:
        raise HTTPException(
            detail="max_price must be greater than 0",
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        )

    for i in range(offset, len(items)):
        if len(filter_items) == limit:
            break
        item = items[i]
        if (
            (show_deleted or not item.deleted)
            and (min_price is None or item.price >= min_price)
            and (max_price is None or item.price <= max_price)
        ):
            filter_items.append(item)

    return filter_items


# PUT
@app.put("/item/{id}", response_model=Item)
def update_item(id: int, item: ItemAdd):
    for i, current in enumerate(items):
        if current.id == id:
            new_item = Item(id=id, name=item.name, price=item.price)
            items[i] = new_item
            return new_item
    raise HTTPException(detail="Item not found", status_code=HTTPStatus.NOT_FOUND)


# PATCH
@app.patch("/item/{id}", response_model=Item)
def patch_item(id: int, update_fields: dict):
    for key in update_fields.keys():
        if not (key in ["name", "price"]):
            raise HTTPException(
                detail=f"Unexpected field {key}",
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            )
    for i, current in enumerate(items):
        if current.id == id:
            if current.deleted:
                raise HTTPException(
                    detail="Cannot change deleted item",
                    status_code=HTTPStatus.NOT_MODIFIED,
                )
            if "deleted" in update_fields:
                raise HTTPException(
                    detail="Cannot change 'deleted' field",
                    status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                )
            item_data = current.dict()
            item_data.update(update_fields)
            patch_item = Item(**item_data)
            items[i] = patch_item
            return patch_item
    raise HTTPException(detail="Item not found", status_code=HTTPStatus.NOT_FOUND)


# DELETE
@app.delete("/item/{id}")
def delete_item(id: int):
    for item in items:
        if item.id == id:
            item.deleted = True
            return {"message": "Item deleted"}
    raise HTTPException(detail="Item not found", status_code=HTTPStatus.NOT_FOUND)


if __name__ == "__main__":
    uvicorn.run("hw_2:app", host="127.0.0.1", port=8000, reload=True)
