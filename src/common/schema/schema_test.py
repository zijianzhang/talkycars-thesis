import capnp

capnp.remove_import_hook()

if __name__ == '__main__':

    vector3d = capnp.load('./capnp/vector3d.capnp')
    relative_bbox = capnp.load('./capnp/relative_bbox.capnp')
    relation = capnp.load('./capnp/relation.capnp')
    ego_vehicle = capnp.load('./capnp/ego_vehicle.capnp')

    me = ego_vehicle.EgoVehicle.new_message()
    me.id = 1
    me.position = relation.Vector3DRelation.new_message()
    me.color = relation.TextRelation.new_message(confidence=1, object='blue')
    me.boundingBox = relation.RelativeBBoxRelation.new_message()
    me.velocity = relation.Vector3DRelation.new_message()
    me.acceleration = relation.Vector3DRelation.new_message()

    # x = lat, y = lon, z = alt
    me.position.object = vector3d.Vector3D.new_message(x=49.472, y=-112.980)
    me.position.confidence = 0.98

    me.boundingBox.object = relative_bbox.RelativeBBox.new_message()
    me.boundingBox.confidence = 1
    me.boundingBox.object.lower = vector3d.Vector3D.new_message(x=-2.56, y=-1.48, z=1.55)
    me.boundingBox.object.higher = vector3d.Vector3D.new_message(x=2.56, y=1.48, z=1.55)

    me.velocity.object = vector3d.Vector3D.new_message(x=0, y=0, z=0)
    me.velocity.confidence = 1

    me.acceleration.object = vector3d.Vector3D.new_message(x=0, y=0, z=0)
    me.acceleration.confidence = 1

    encoded_me = me.to_bytes_packed()
    print(f'Encoded to {len(encoded_me)} bytes.')

    decoded_me = ego_vehicle.EgoVehicle.from_bytes_packed(encoded_me)
    print(decoded_me)