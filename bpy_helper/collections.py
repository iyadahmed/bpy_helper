# This is needed to find "Layer Collection" of a Collection, which is used to hide the collection
def find_layer_collection_recursive(parent_layer_collection, collection):
    if parent_layer_collection.collection == collection:
        return parent_layer_collection

    for layer_collection in parent_layer_collection.children:
        return find_layer_collection_recursive(layer_collection, collection)


def collection_hide_inside(context, collection):
    layer_collection = find_layer_collection_recursive(context.view_layer.layer_collection, collection)
    layer_collection.hide_viewport = True
    for obj in collection.all_objects:
        obj.hide_set(True)
    for col in collection.children:
        collection_hide_inside(context, col)
