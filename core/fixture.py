def script():

    import json

    from core.models import Department, Property, InventoryList, MOL
    with open('core/info.json', encoding='utf-8') as file:
        request = json.loads(file.read())

    for corp in request.values():
        for item in corp:
            # print(item['cabinet'])
            print(bool(Department.objects.filter(cabinet=123).first()))
            if not Department.objects.filter(cabinet=item['cabinet']).first():
                print(1)
                department = Department(cabinet=item['cabinet'], organization_id=1).save()
                print(department)
                print(2)
                sa = MOL(department=Department.objects.filter(cabinet=item['cabinet']).first(), FIO=(item['cabinet'])).save()
                print(3)
                # print(MOL.objects.filter(department=department))
            # print(bool(Department.objects.filter(cabinet=item['cabinet']).first()))
            if not Property.objects.filter(name=item['name']).first():
                property = Property(name=item['name']).save()
            if item.get('invent_num') is not None and not InventoryList.objects.filter(invent_num=item.get('invent_num')).first():
                InventoryList(property=Property.objects.filter(name=item['name']).first(), MOL=MOL.objects.filter(department__cabinet=item['cabinet']).first(),
                                             description=item.get('description', ''), invent_num=item.get('invent_num', ''), amount=1).save()

            elif not InventoryList.objects.filter(description=item.get('description', ''), property__name=item['name'],
                                                  MOL__department__cabinet=item['cabinet']).first():
                InventoryList(description=item.get('description', ''), property=Property.objects.filter(name=item['name']).first(),
                              MOL=MOL.objects.filter(department__cabinet=item['cabinet']).first(), amount=1).save()

            elif inv := InventoryList.objects.filter(property__name=item['name'], MOL__department__cabinet=item['cabinet'],
                                                     description=item.get('description', '')).first():
                inv.amount += 1
                inv.save()

            else:
                invent_list = InventoryList.objects.filter(invent_num=item.get('invent_num')).first()
                print(invent_list)
                print('_')
                invent_list.amount += 1
                invent_list.save()

    for obj in Department.objects.all():
        obj.name = obj.cabinet
        obj.save()

# script()