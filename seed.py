import asyncio
from app.database import init_db, async_session
from app.models.user import User, UserRole
from app.models.mechanic import MechanicProfile, MechanicSpecialty, Specialty, MechanicPhoto
from app.models.review import Review
from app.models.tutorial import Tutorial
from app.models.service import Service
from app.auth import hash_password


async def seed():
    await init_db()
    async with async_session() as db:
        existing = await db.execute(User.__table__.select().limit(1))
        if existing.first():
            print("La base de datos ya tiene datos. Omitiendo seed.")
            return

        specs_data = [
            "Motor", "Frenos", "Suspensión", "Transmisión", "Eléctrico",
            "Aire Acondicionado", "Diagnóstico", "Hojalatería", "Pintura",
            "Afinación", "Clutch",             "Dirección Hidráulica", "Sistemas de Inyección",
            "Escape", "Refrigeración", "Alineación"
        ]
        specs = {}
        for name in specs_data:
            spec = Specialty(name=name)
            db.add(spec)
            await db.flush()
            specs[name] = spec.id

        mechanics_data = [
            {
                "name": "Carlos Méndez", "email": "carlos@email.com", "phone": "555-100-2000",
                "business": "Taller Méndez", "desc": "Especialista en motores europeos con más de 15 años de experiencia. Diagnóstico computarizado y reparación de alta calidad.",
                "years": 15, "location": "Ciudad de México, Centro", "lat": 19.4326, "lng": -99.1332,
                "specs": ["Motor", "Diagnóstico", "Sistemas de Inyección", "Eléctrico"],
                "reviews": [
                    (5, "Excelente servicio, diagnosticó un problema que otros no pudieron. Muy recomendado."),
                    (4, "Buen trabajo, tardó un poco más de lo esperado pero quedó bien."),
                    (5, "El mejor mecánico de la zona. Honesto y conocedor."),
                    (4, "Me explicó todo antes de hacerlo, se agradece la transparencia."),
                ]
            },
            {
                "name": "María López", "email": "maria@email.com", "phone": "555-200-3000",
                "business": "Taller Hermanos López", "desc": "Especialista en frenos y suspensión. Mujer al volante, mecánica de confianza. Precios justos y trabajo garantizado.",
                "years": 10, "location": "Monterrey, Nuevo León", "lat": 25.6866, "lng": -100.3161,
                "specs": ["Frenos", "Suspensión", "Dirección Hidráulica", "Refrigeración"],
                "reviews": [
                    (5, "María es increíble, le arregló los frenos a mi camioneta en un día. Precio justo."),
                    (5, "Muy profesional y honesta. Le hizo mantenimiento a mi coche y quedó como nuevo."),
                    (3, "Buen servicio pero tardaron en conseguir una pieza."),
                ]
            },
            {
                "name": "Juan Martínez", "email": "juan@email.com", "phone": "555-300-4000",
                "business": "Martínez Transmisiones", "desc": "Expertos en transmisiones automáticas y estándar. 20 años de experiencia. Garantía por escrito en todos los trabajos.",
                "years": 20, "location": "Guadalajara, Jalisco", "lat": 20.6597, "lng": -103.3496,
                "specs": ["Transmisión", "Clutch", "Motor", "Afinación"],
                "reviews": [
                    (5, "Le cambiaron la transmisión a mi Honda y quedó perfecta. Tienen garantía."),
                    (5, "Muy recomendado. Me salvó con el clutch en un día."),
                    (4, "Buen trabajo, pero el precio fue un poco alto. Aunque la calidad lo vale."),
                    (5, "Juan sabe lo que hace. Confianza total."),
                ]
            },
            {
                "name": "Roberto Sánchez", "email": "roberto@email.com", "phone": "555-400-5000",
                "business": "Sánchez Electric Auto", "desc": "Diagnóstico eléctrico especializado. Sistemas de inyección, sensores, ECU y sistemas electrónicos modernos.",
                "years": 8, "location": "Puebla, Puebla", "lat": 19.0414, "lng": -98.2063,
                "specs": ["Eléctrico", "Diagnóstico", "Sistemas de Inyección"],
                "reviews": [
                    (4, "Resolvió un problema eléctrico que traía desde hace meses."),
                    (5, "Muy conocedor de electrónica automotriz. Lo recomiendo ampliamente."),
                ]
            },
            {
                "name": "Ana Torres", "email": "ana@email.com", "phone": "555-500-6000",
                "business": "Taller Ana Torres", "desc": "Hojalatería y pintura de calidad. Reparación de carrocería, cambios de piezas y pintura original. Trabajo con seguros.",
                "years": 12, "location": "Querétaro, Querétaro", "lat": 20.5888, "lng": -100.3899,
                "specs": ["Hojalatería", "Pintura", "Suspensión"],
                "reviews": [
                    (5, "Dejó mi coche como nuevo después del choque. La pintura quedó idéntica."),
                    (5, "Ana hace magia con la carrocería. Muy recomendada."),
                    (4, "Buen trabajo, cumplió en el tiempo prometido."),
                    (5, "Excelente atención y resultado. Trabaja con el seguro sin problema."),
                ]
            },
            {
                "name": "Pedro García", "email": "pedro@email.com", "phone": "555-600-7000",
                "business": "García Aire y Más", "desc": "Especialista en aire acondicionado automotriz. También hago mantenimiento general, afinaciones y diagnóstico.",
                "years": 7, "location": "Tijuana, Baja California", "lat": 32.5149, "lng": -117.0382,
                "specs": ["Aire Acondicionado", "Refrigeración", "Afinación", "Diagnóstico"],
                "reviews": [
                    (5, "El aire de mi coche no enfriaba desde hace años. Pedro lo dejó funcionando perfecto."),
                    (4, "Buen servicio, precio razonable. Volvería."),
                ]
            },
            {
                "name": "Luis Hernández", "email": "luis@email.com", "phone": "555-700-8000",
                "business": "Hernández Motores", "desc": "Reparación y reconstrucción de motores a gasolina y diésel. Rectificación, cambio de anillos, empaques, cabezas y más.",
                "years": 18, "location": "Mérida, Yucatán", "lat": 20.9674, "lng": -89.5926,
                "specs": ["Motor", "Sistemas de Inyección", "Escape", "Refrigeración"],
                "reviews": [
                    (5, "Reconstruyó el motor de mi camioneta y quedó mejor que nueva. Un maestro."),
                    (5, "Luis es un experto. Le confié mi motor sin dudar."),
                    (4, "Muy buen trabajo, me mantuvo informado en todo el proceso."),
                    (5, "Honesto y conocedor. Precio justo por un trabajo tan especializado."),
                ]
            },
            {
                "name": "Gabriela Ruiz", "email": "gabriela@email.com", "phone": "555-800-9000",
                "business": "Ruiz Suspensión y Dirección", "desc": "Especialista en suspensión, dirección y frenos. Alineación y balanceo. Atención a mujeres conductoras.",
                "years": 6, "location": "Cancún, Quintana Roo", "lat": 21.1619, "lng": -86.8515,
                "specs": ["Suspensión", "Dirección Hidráulica", "Frenos", "Alineación"],
                "reviews": [
                    (5, "Excelente servicio, me explicó todo y no me cobró de más por ser mujer."),
                    (4, "Cambió la suspensión de mi coche y quedó muy bien."),
                    (5, "Gabriela es muy profesional. Recomiendo ampliamente."),
                ]
            },
            {
                "name": "Fernando Castillo", "email": "fernando@email.com", "phone": "555-900-1000",
                "business": "Castillo Performance", "desc": "Diagnóstico con escáner profesional. Reparación de ECU, sistemas eléctricos complejos, y modificaciones de rendimiento.",
                "years": 9, "location": "Toluca, Estado de México", "lat": 19.2826, "lng": -99.6557,
                "specs": ["Diagnóstico", "Eléctrico", "Sistemas de Inyección", "Motor"],
                "reviews": [
                    (4, "Muy buen diagnóstico, encontró una falla intermitente que nadie más pudo."),
                    (5, "Fernando es un crack con la electrónica. Salvó mi coche."),
                    (4, "Buen servicio, aunque la consulta es un poco cara."),
                ]
            },
            {
                "name": "Diego Ramírez", "email": "diego@email.com", "phone": "555-111-2222",
                "business": "Ramírez Frenos y Clutch", "desc": "Expertos en frenos, clutch y transmisión. Cambio de pastillas, discos, líquido de frenos, kits de clutch. Servicio rápido.",
                "years": 14, "location": "Ciudad de México, Norte", "lat": 19.5123, "lng": -99.1287,
                "specs": ["Frenos", "Clutch", "Transmisión", "Afinación"],
                "reviews": [
                    (5, "Le cambié los frenos y el clutch a mi Jetta. Quedó perfecto y a buen precio."),
                    (5, "Servicio rápido y de calidad. Lo recomiendo ampliamente."),
                    (4, "Hicieron el trabajo en el tiempo prometido. Buena atención."),
                    (5, "Diego es muy honesto, me dijo lo que realmente necesitaba y no me vendió cosas extras."),
                ]
            },
        ]

        services_seed = [
            ["Cambio de Aceite y Filtro", "Cambio de aceite sintético con filtro incluido. Revisión de niveles general.", 350, "Mantenimiento", "1 hora"],
            ["Diagnóstico Computarizado", "Escaneo completo del sistema electrónico del vehículo. Códigos de error y reporte detallado.", 500, "Diagnóstico", "1 hora"],
            ["Reparación de Frenos", "Cambio de pastillas, discos y líquido de frenos. Revisión del sistema completo.", 1200, "Frenos", "4 horas"],
            ["Cambio de Clutch", "Reemplazo de kit de clutch completo. Incluye volante si es necesario.", 3500, "Transmisión", "1 día"],
            ["Afinación Completa", "Cambio de bujías, filtros, aceite y revisión general del motor.", 800, "Mantenimiento", "2 horas"],
            ["Reparación de Aire Acondicionado", "Diagnóstico y recarga de gas. Reparación de fugas y componentes.", 1500, "Aire Acondicionado", "4 horas"],
            ["Suspensión Completa", "Cambio de amortiguadores, resortes y brazos de suspensión.", 2500, "Suspensión", "1 día"],
            ["Rectificación de Motor", "Reparación mayor de motor: anillos, empaques, rectificación de cabezas.", 8000, "Motor", "1 semana"],
            ["Sistema Eléctrico", "Reparación de sistema eléctrico, alternador, arranque y sensores.", 900, "Eléctrico", "4 horas"],
            ["Hojalatería y Pintura", "Reparación de carrocería, enderezado y pintura original.", 3000, "Hojalatería", "2-3 días"],
        ]

        for i, md in enumerate(mechanics_data):
            user = User(
                email=md["email"], password=hash_password("123456"),
                name=md["name"], phone=md["phone"], role=UserRole.MECHANIC,
            )
            db.add(user)
            await db.flush()

            profile = MechanicProfile(
                user_id=user.id, business_name=md["business"],
                description=md["desc"], years_experience=md["years"],
                location=md["location"], latitude=md["lat"], longitude=md["lng"],
                available=True, verified=(i % 3 == 0),
            )
            db.add(profile)
            await db.flush()

            for spec_name in md["specs"]:
                db.add(MechanicSpecialty(mechanic_id=profile.id, specialty_id=specs[spec_name]))

            for ri, (rating, comment) in enumerate(md["reviews"]):
                client_user = User(
                    email=f"client{i}_{ri}@email.com",
                    password=hash_password("123456"),
                    name=f"Cliente de {md['name']}",
                    role=UserRole.CLIENT,
                )
                db.add(client_user)
                await db.flush()
                review = Review(
                    mechanic_id=profile.id, client_id=client_user.id,
                    rating=rating, comment=comment,
                )
                db.add(review)

            svc_data = services_seed[i % len(services_seed)]
            service = Service(
                mechanic_id=profile.id,
                title=svc_data[0],
                description=svc_data[1],
                price=svc_data[2],
                category=svc_data[3],
                duration=svc_data[4],
            )
            db.add(service)

            tutorial = Tutorial(
                mechanic_id=profile.id,
                title=f"Cómo cambiar {md['specs'][0].lower()} - Tutorial por {md['name']}",
                description=f"Aprende los pasos básicos para el mantenimiento y reparación de {md['specs'][0].lower()} en tu vehículo. {md['name']} con {md['years']} años de experiencia te guía paso a paso.",
                content=f"<p>En este tutorial aprenderás todo lo básico sobre <strong>{md['specs'][0].lower()}</strong> en tu vehículo.</p><h3>¿Qué necesitas?</h3><ul><li>Herramientas básicas</li><li>Manual de tu vehículo</li><li>Piezas de repuesto originales o de calidad</li></ul><h3>Pasos a seguir</h3><p>1. Identifica el problema correctamente.</p><p>2. Reúne las herramientas necesarias.</p><p>3. Sigue el procedimiento de seguridad (desconectar batería si es necesario).</p><p>4. Realiza el trabajo con cuidado.</p><p>5. Prueba antes de dar por terminado.</p><p>Recuerda: si no te sientes seguro, siempre es mejor acudir a un profesional. El diagnóstico correcto es la mitad del trabajo bien hecho.</p>",
                category=md["specs"][0], difficulty="Intermedio",
            )
            db.add(tutorial)

        await db.commit()
        print(f"Seed completado: {len(mechanics_data)} mecanicos creados con resenas y tutoriales.")
        print("Usuarios para prueba (todos con contrasena: 123456):")
        for md in mechanics_data:
            print(f"  - {md['email']}")

if __name__ == "__main__":
    asyncio.run(seed())
