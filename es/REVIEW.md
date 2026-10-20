# autoants en español: wording review

Branch `es` (not merged). Built 2026-10-20 from Lane's approval the same day. **224 strings** below, numbered, every
visible Spanish string on the 5 pages plus each page's `<title>` and meta description, the form's placeholder and error
text, and the JSON-LD description. A string shared by several pages (nav, the support block, the business facts,
the footer) is listed once, on the first page it appears on.

Nothing here is published: every page carries the banner "Borrador: revisión humana pendiente" and `noindex`, and none
is in `sitemap.xml`.

## Who reviews, and how

A **fluent Spanish reader** (ideally someone who sells to or works in the trades around Kenner, Metairie or the West
Bank) reads every numbered string and marks it OK, or writes the better wording beside it. Register: **usted**,
plain words, Latin American Spanish as spoken in the New Orleans area, nothing Spain-only. The pages were written
for Spanish search intent, not translated sentence by sentence, so judge them as Spanish, not against the English.

Things to check hardest:
- The door names (glossary below): do they read as natural Spanish to a shop owner?
- Trade words: "techeros", "técnicos de aire acondicionado", "colgadores de puerta", "Ribera Oeste" (West Bank).
- That the receptionist is always "un asistente de inteligencia artificial" and never sounds like a person.
- No promise of results, no "#1", no "el mejor", no "garantizado". The only promise is the $500 back (Pruebe uno).
- Every price matches `tle-main/docs/playbooks/offer-map.md` exactly (checked 2026-10-20; no price ends in 9).

Record the approval here (the day the reviewer actually did it; ask, don't infer):

| Reviewer | Date | Strings approved | Notes |
|---|---|---|---|
| | | | |

## Glossary (door names, used everywhere)

| English (offer-map) | Spanish on these pages |
|---|---|
| Free breakdown | Análisis gratis (de su negocio) |
| Get found | Que lo encuentren |
| Never miss a job | No pierda trabajos |
| Get found and never miss a job | Que lo encuentren y no pierda trabajos |
| Add-on: Get the next job | Extra: el próximo trabajo |
| Try one | Pruebe uno |
| AI receptionist | Contestador: un asistente de inteligencia artificial que contesta |
| Missed-call text-back | El texto a la llamada perdida |

## Decisions for Lane before merge

1. **[LANE: decide] Spanish support.** No fluent Spanish speaker is available today (Lane does not speak Spanish
   fluently; same finding as the succession-firm ES decision of 2026-08-11). The pages say so honestly: written
   Spanish yes, calls with Lane in English for now, bring a bilingual person if you like. Pick one: (a) written-only
   Spanish (AI-drafted, reviewed); (b) a professional phone interpreter booked per sales and setup meeting;
   (c) a bilingual hire or partner. Then edit the support block and the "Idiomas" fact, and delete the yellow note.
   The JSON-LD `contactPoint.availableLanguage` lists Spanish; drop it if (a) is not chosen either.
2. **[PROPUESTO] prices shown on draft pages:** the AI receptionist ($750/mo + $500 setup, 300 min, then $0.50/min)
   and the language pack ($500 setup + $100/mo). Both are PROPOSED in offer-map. Confirm or delete those yellow notes.
3. **"Le respondemos por correo electrónico en español"** (the form page) is a promise. Keep it only if decision 1
   covers written Spanish replies.
4. **The form sends no texts.** autoants' own 10DLC campaign is English only (`tle-main/products/spanish-ants/10DLC-spanish.md`),
   so the Spanish form has no SMS opt-in box; it asks for email instead. The privacy policy and terms stay English
   (no machine-only translation of legal notices, language-pack rule LP3); the pages say so.
5. **The "6 de 8" stat** (two national franchises in Spanish AI answers about Kenner HVAC) comes from one Claude run
   on 2026-10-20 (tle-main `data/aivis/kenner/hvac-es/market-2026-10.json`). Answers vary; re-run before publishing
   and keep the date beside it. The 98% stat is a homepage-only first pass (`data/language-targeting/stats-2026-10-20.md`);
   tle-main's rule is that a person checks in a browser before it's said to an owner.
6. **Fluent reviewer** named and booked (who and when).
7. **Noticed in passing:** the English `/prices/` on `main` still shows the older after-founding prices (both $1,750);
   offer-map changed them on 2026-10-20 (both $2,000 + $2,000 setup, add-on +$1,500). The Spanish page follows
   offer-map; the English page needs the same fix (branch `prices-2026-10-20` may already have it).

## Merge checklist (after approval)

- Remove the `.draft` banner div and `<meta name="robots" content="noindex">` from the 5 pages.
- Delete the yellow `.note` blocks (decisions above), and the footer line "Revisión humana pendiente" becomes
  "…y la revisó <nombre> el <fecha>."
- Add the 5 `/es/` URLs to `sitemap.xml`.
- hreflang is already reciprocal: `/` ↔ `/es/`, `/prices/` ↔ `/es/precios/`, `/services.html` ↔ `/es/que-hacemos/`
  (EN pages carry en-US, es-US and x-default). `/es/analisis-gratis/` and `/es/contestador-de-llamadas/` have no
  English twin, so they carry only their own es-US tag.
- Delete this file from the branch (it is served as plain text otherwise; the site has `.nojekyll`).

## The strings

### `es/index.html` (72)

1. Asistente de IA para contratistas en Nueva Orleans y Kenner · autoants
2. [meta description] Contestamos las llamadas que usted pierde y lo ayudamos a aparecer en Google. Para plomeros, técnicos de aire acondicionado, techeros y otros oficios en Nueva Orleans, Kenner y Metairie. Análisis gratis para empezar.
3. Borrador: revisión humana pendiente
4. Inicio
5. Qué hacemos
6. Precios
7. Contestador en español
8. English
9. autoants en español · para dueños de negocios de oficios
10. Asistente de IA para contratistas en Nueva Orleans y Kenner.
11. Contestamos las llamadas que usted pierde y lo ayudamos a que lo encuentren en Google: $1,250 al mes. ¿Todavía no está listo? Pruebe un asistente por $500.
12. Para plomeros, técnicos de aire acondicionado, techeros, electricistas, jardineros y otros oficios en Nueva Orleans, Kenner, Metairie y la Ribera Oeste.
13. Pida su análisis gratis
14. Ver precios
15. El problema
16. Usted está en un trabajo. Suena el teléfono. No puede contestar.
17. Ese cliente no deja mensaje: llama al siguiente nombre que le sale en Google. Nosotros le contestamos por usted en segundos, por texto, en inglés o en español, y le pasamos los datos para que usted decida.
18. Que lo encuentren
19. Aparezca en Google y en las respuestas de IA
20. Su perfil de Google al día y con una publicación cada semana, sus listados correctos, 2 páginas nuevas al mes y una revisión mensual de lo que dicen de usted los asistentes de inteligencia artificial.
21. No pierda trabajos
22. Cada llamada perdida recibe respuesta
23. Texto automático a cada llamada que usted no contesta, seguimiento de cotizaciones, citas con recordatorio y la petición de reseña después de cada trabajo.
24. El próximo trabajo
25. Los vecinos y sus clientes de antes
26. Publicaciones y videos cortos de sus trabajos reales, tarjetas postales a los vecinos y a sus clientes de antes, y colgadores de puerta alrededor de cada trabajo. Es un extra para después.
27. Vea todo lo que incluye →
28. Lo que medimos
29. En español, casi nadie está contestando.
30. de las personas de 5 años o más en Jefferson Parish hablan español en casa. El 7.3% habla inglés menos que muy bien.
31. Fuente: Censo de EE. UU., ACS 2020–2024, tabla C16001.
32. de 135 sitios web de compañías de aire acondicionado que revisamos en Orleans, Jefferson y St. Bernard no tenían una página en español desde su página principal.
33. Revisión de autoants, octubre de 2026. Una lectura por sitio.
34. 6 de 8
35. respuestas en español sobre aire acondicionado en Kenner nombraron a las mismas dos franquicias nacionales. Las compañías locales casi no aparecieron.
36. 8 preguntas en español a un asistente de IA (Claude), 20 de octubre de 2026. Las respuestas cambian de un día a otro.
37. Su análisis gratis le muestra dónde está usted en Google y en las respuestas de IA, en inglés y en español. No prometemos resultados: medimos antes y después, y se lo enseñamos.
38. Para sus clientes que hablan español
39. Su contestador también habla español.
40. El texto a las llamadas perdidas, los recordatorios y la petición de reseña pueden salir en español. Y si usted quiere una voz que conteste, un asistente de inteligencia artificial contesta, dice que es un asistente de inteligencia artificial, pregunta "¿Prefiere español?", toma los datos y le manda un texto a usted.
41. Cómo funciona el contestador en español →
42. Cómo trabajamos
43. Primero hacemos el trabajo. Usted decide después.
44. 1. Análisis gratis
45. Un análisis de su negocio de 10 a 14 páginas, hecho con información pública: cómo aparece en Google, en las respuestas de IA y al lado de su competencia.
46. 2. Usted escoge
47. El análisis le dice qué arreglo necesitan sus números. Sin contrato para empezar.
48. 3. Pruebe uno
49. Un asistente en su teléfono, funcionando en 7 días, o le devolvemos sus $500.
50. En español
51. Cómo le atendemos en español
52. Puede escribirnos en español: por el formulario o a hello@autoants.com. Esta página, su análisis gratis y los mensajes que reciben sus clientes pueden ir en español.
53. Le decimos la verdad: Lane, el fundador, no habla español con fluidez. Las llamadas y reuniones con él son en inglés por ahora. Si lo prefiere, traiga a alguien de su confianza que hable los dos idiomas.
54. [LANE: decide] Soporte en español: hoy no hay una persona que hable español con fluidez. Antes de publicar, decida una opción: (a) solo por escrito en español, redactado con ayuda de inteligencia artificial y revisado; (b) un intérprete profesional por llamada para reuniones de venta y de instalación; (c) una persona bilingüe contratada o socia. Este aviso se borra al decidir; el texto de arriba se ajusta a lo decidido. _(internal note: delete before merge, do not review the wording)_
55. Datos del negocio
56. Nombre
57. autoants (AutoAnts, LLC)
58. Qué es
59. Asistentes automatizados y presencia en Google para negocios locales de oficios
60. Zona
61. Nueva Orleans, Metairie, Kenner, Slidell, Baton Rouge y el resto de Luisiana
62. Correo
63. hello@autoants.com
64. Idiomas
65. Español por escrito; llamadas con Lane en inglés por ahora
66. Fundador
67. Lane Davis II
68. autoants, asistentes automatizados · Luisiana ·
69. Análisis gratis
70. Lo que nunca hace (en inglés)
71. Privacidad (en inglés)
72. Esta página se escribió en español con ayuda de inteligencia artificial. Revisión humana pendiente.

### `es/que-hacemos/index.html` (40)

73. Asistente de IA para contratistas: llamadas, Google y clientes nuevos · autoants
74. [meta description] Qué hace autoants por un negocio de oficios en Nueva Orleans: que lo encuentren en Google, que no pierda trabajos por llamadas sin contestar, y el próximo trabajo de los vecinos y sus clientes de antes.
75. Asistente de IA para contratistas: tres cosas, en su idioma.
76. Contestamos las llamadas que usted pierde, le damos seguimiento a las cotizaciones que se le olvidan y lo ayudamos a que los clientes lo encuentren en Google. Así más del trabajo que usted ya paga se convierte en trabajos agendados.
77. 1 · Que lo encuentren
78. Aparezca cuando lo buscan, en Google y en los asistentes de IA.
79. Para el negocio que hace buen trabajo pero no sale en el mapa ni en las respuestas de inteligencia artificial.
80. Su perfil de Google al día, con una publicación cada semana hecha con fotos de sus trabajos reales. Usted la aprueba por texto antes de que salga.
81. Sus listados correctos (Google, Apple, Bing, Yelp y otros).
82. 2 páginas nuevas al mes para su sitio: un servicio en una ciudad, o una respuesta a lo que preguntan sus clientes.
83. Cada mes revisamos lo que dicen de usted los asistentes de inteligencia artificial.
84. Respuestas a sus reseñas, escritas para que usted las revise.
85. Su sitio web hospedado y al día.
86. 2 · No pierda trabajos
87. Cada llamada perdida recibe respuesta en segundos.
88. Para el negocio que sí aparece, pero las llamadas suenan y nadie contesta porque usted está trabajando.
89. Un texto automático a cada llamada que usted no contesta, en inglés o en español.
90. Respuesta a los formularios de su sitio y a los mensajes de Facebook e Instagram.
91. Seguimiento de las cotizaciones que usted mandó y se le olvidaron.
92. Citas agendadas, con recordatorio.
93. La petición de reseña después de cada trabajo.
94. Un botón de "agendar ahora" en su sitio.
95. ¿Quiere que una voz conteste cuando usted no puede? Eso es el contestador: un asistente de inteligencia artificial que siempre dice que es un asistente de inteligencia artificial.
96. 3 · El próximo trabajo
97. Que los vecinos y sus clientes de antes se acuerden de usted.
98. Es un extra, solo encima de los dos primeros, para el negocio que ya tiene fotos de trabajos reales.
99. Publicaciones y videos cortos cada semana, de sus trabajos reales.
100. Tarjetas postales a los vecinos del trabajo que usted acaba de hacer.
101. Colgadores de puerta alrededor de cada trabajo.
102. Tarjetas postales a sus clientes de antes.
103. Ofertas para las personas que acaban de comprar casa cerca de usted.
104. Para sus clientes
105. Su negocio, también en español.
106. De 135 sitios web de compañías de aire acondicionado que revisamos en Orleans, Jefferson y St. Bernard en octubre de 2026, el 98% no tenía una página en español desde su página principal. Si usted la tiene, se nota.
107. Páginas en español escritas para cómo buscan sus clientes ("plomero en Kenner", "reparación de aire acondicionado en Metairie"), no copiadas palabra por palabra del inglés.
108. Su perfil de Google y sus listados con texto en español.
109. El texto a llamadas perdidas y la petición de reseña en español.
110. Una revisión de quién aparece cuando alguien pregunta en español a un asistente de IA.
111. La inteligencia artificial escribe y una persona revisa. Sus precios, horarios y garantías dicen lo mismo en los dos idiomas.
112. [PROPUESTO] Precio del paquete en español: $500 de instalación + $100 al mes, o incluido en "Que lo encuentren y no pierda trabajos". Pendiente de que Lane lo confirme; se borra o se confirma antes de publicar. _(internal note: delete before merge, do not review the wording)_

### `es/precios/index.html` (41)

113. Precios: asistente de IA y contestador de llamadas para contratistas · autoants
114. [meta description] Precios de autoants: $1,250 al mes para contestar las llamadas que usted pierde y aparecer en Google, o pruebe un asistente por $500. Todos los precios y cuotas de instalación en una página.
115. Dos maneras de empezar.
116. Primero, gratis: un análisis de su negocio. Cómo aparece en Google, en las respuestas de IA y al lado de su competencia. Le dice qué arreglo necesitan sus números.
117. Empiece aquí
118. Que lo encuentren y no pierda trabajos
119. $1,250 al mes + $1,000 de instalación
120. Contestamos las llamadas que usted pierde y lo ayudamos a que lo encuentren en Google. Llamadas perdidas contestadas, cotizaciones con seguimiento, citas agendadas y con recordatorio, reseñas pedidas, su perfil de Google al día y con una publicación cada semana, sus listados correctos, 2 páginas nuevas al mes, una revisión mensual de lo que dicen de usted los asistentes de IA, y su sitio web al día. Además, un paquete del mercado cada mes: su parte de los permisos, los trabajos que les tocan a sus clientes de antes, páginas de sus vecindarios y un ojo sobre su competencia.
121. ¿Todavía no?
122. Pruebe uno
123. $500 una sola vez
124. Un asistente en su teléfono, funcionando en 7 días después de que usted diga que sí (para textos, 7 días después de la aprobación de las compañías telefónicas), o le devolvemos sus $500.
125. Letra pequeña, en palabras claras
126. Todo es suyo: sus cuentas, sus páginas y su lista de clientes.
127. 90 días, después mes a mes. Cancela por correo electrónico.
128. No prometemos resultados. Contamos sus llamadas y sus trabajos antes y después, y se los mostramos cada mes.
129. Los precios son para nuestros primeros 3 negocios.
130. El contrato y los términos legales están en inglés.
131. Otras opciones
132. Si su análisis dice que necesita solo una cosa
133. $750 al mes + $750 de instalación
134. Solo las llamadas: llamadas perdidas contestadas, cotizaciones con seguimiento, citas agendadas y con recordatorio, reseñas pedidas, mensajes de Facebook e Instagram contestados, y un botón de "agendar ahora" en su sitio.
135. $750 al mes + $250 de instalación
136. Solo Google: su perfil de Google al día y con una publicación cada semana, sus listados correctos, 2 páginas nuevas al mes, una revisión mensual de lo que dicen de usted los asistentes de IA, respuestas a reseñas escritas para usted, y su sitio web al día.
137. ¿Necesita las dos? "Que lo encuentren y no pierda trabajos" cuesta $1,250 al mes. Son $250 al mes menos que comprarlas por separado.
138. Pagar por trabajo
139. ¿Prefiere pagar por trabajo? "No pierda trabajos" también se puede pagar así: $250 al mes + $25 por cada trabajo que salvamos de una llamada que usted no contestó. Solo cuenta un trabajo terminado y pagado. Nunca más de $750 al mes.
140. Extra: el próximo trabajo
141. + $1,250 al mes + $500 de instalación
142. Redes sociales y mercadeo, encima de las dos: publicaciones y videos cortos cada semana de sus trabajos reales, tarjetas postales a los vecinos, colgadores de puerta alrededor de cada trabajo, tarjetas postales a sus clientes de antes, y ofertas para las personas que acaban de comprar casa cerca de usted. En total: $2,500 al mes y $1,500 de instalación. Tarjetas postales: $1.30 cada una.
143. Contestador: un asistente de inteligencia artificial que contesta
144. Cuando usted no puede contestar, un asistente de inteligencia artificial contesta, toma los datos y le manda un texto. Siempre dice que es un asistente de inteligencia artificial. Solo, o encima de cualquier plan. Cómo funciona →
145. [PROPUESTO] $750 al mes + $500 de instalación; 300 minutos incluidos, después $0.50 por minuto. Pendiente de que Lane lo confirme; se borra o se confirma antes de publicar. _(internal note: delete before merge, do not review the wording)_
146. Sitio web nuevo
147. $1,000 una sola vez
148. Hasta 5 páginas, hechas para usted. El sitio y su dominio son suyos. Gratis cuando empieza "Que lo encuentren y no pierda trabajos". Después, por $100 al mes lo mantenemos hospedado y al día, o usted se lleva los archivos adonde quiera.
149. Operaciones grandes y el análisis impreso
150. Operations Math by autoants: para operaciones grandes (rutas, horarios, cortes y cargas). Prueba de 30 días por $1,500, que se acredita al primer mes. Después, el precio va según el tamaño de la operación y se escribe en el contrato.
151. El análisis impreso: $500. Una entrevista grabada de 45 minutos y un informe impreso y encuadernado. Se acredita a la instalación si usted sigue en 30 días.
152. Después de nuestros primeros 3 negocios
153. Los precios de arriba son para nuestros primeros 3 negocios. Después: "No pierda trabajos" cuesta $1,000 al mes + $1,500 de instalación; "Que lo encuentren", $1,000 al mes + $500 de instalación; "Que lo encuentren y no pierda trabajos", $2,000 al mes + $2,000 de instalación; el extra "El próximo trabajo", + $1,500 al mes + $1,000 de instalación ($3,500 al mes en total). "Pruebe uno" pasa a $750, y pagando por trabajo lo más que paga en un mes pasa a $1,000.

### `es/analisis-gratis/index.html` (38)

154. Análisis gratis de su negocio: Google, IA y su competencia · autoants
155. [meta description] Pida un análisis gratis de su negocio de oficios en Nueva Orleans, Kenner o Metairie: cómo aparece en Google, en las respuestas de inteligencia artificial y al lado de su competencia. Sin compromiso.
156. Gratis, sin compromiso
157. Análisis gratis de su negocio en Google y en las respuestas de IA.
158. De 10 a 14 páginas sobre su negocio, hechas con información pública. Antes de que usted pague nada.
159. Qué le mostramos
160. Cómo aparece usted en Google y en el mapa.
161. Qué dicen de usted los asistentes de inteligencia artificial, en inglés y en español.
162. Cómo se ve usted al lado de su competencia.
163. Qué arreglo necesitan sus números, y cuál no.
164. Qué no hacemos
165. No le pedimos contraseñas para hacerlo.
166. No le prometemos resultados ni un primer lugar.
167. No vendemos ni compartimos sus datos.
168. Si no le sirve, se queda con el análisis y ya.
169. Pídalo aquí
170. Cuéntenos de su negocio.
171. Escriba en español o en inglés, como prefiera. Le respondemos por correo electrónico en español.
172. Su nombre
173. Nombre del negocio
174. Teléfono
175. Correo electrónico
176. Tipo de negocio
177. Oficios para el hogar (aire, plomería, techos, electricidad...)
178. Taller de autos
179. Salón o barbería
180. Gimnasio
181. Otro
182. Me interesa
183. El análisis gratis
184. Pruebe uno ($500)
185. Otra cosa
186. [placeholder] Por ejemplo: perdemos llamadas cuando estamos en un trabajo
187. ¿Algo que debamos saber?
188. Usamos sus datos solo para responder a esta solicitud. No los vendemos ni los compartimos. Nuestra política de privacidad está en inglés.
189. Enviar
190. Recibido. Le respondemos pronto.
191. [JS] No se pudo enviar. Sus datos siguen aquí; intente otra vez en un minuto.

### `es/contestador-de-llamadas/index.html` (32)

192. Contestador de llamadas en español para plomeros y contratistas · autoants
193. [meta description] Contestador de llamadas en español para plomeros, técnicos de aire acondicionado y contratistas en Nueva Orleans y Kenner: texto automático a cada llamada perdida y un asistente de inteligencia artificial que contesta y dice que lo es.
194. Contestador de llamadas en español para plomeros y contratistas.
195. Cuando usted no puede contestar, su cliente recibe respuesta en su idioma: un texto en segundos o, si usted lo quiere, un asistente de inteligencia artificial que contesta la llamada y dice que es un asistente de inteligencia artificial.
196. 1 · El texto a la llamada perdida
197. Una llamada que usted no contesta recibe un texto en segundos.
198. Si el cliente escribe en español, le seguimos respondiendo en español. Si escribe en inglés, en inglés. Así se ve, con un negocio inventado:
199. TEXTO · EJEMPLO
200. Hola, le habla Carlos de Aire del Lago. Perdón por no contestar; estamos en otra llamada. ¿El aire no enfría, no prende o está goteando? Dígame eso y sus calles cercanas y le mando un horario hoy. Responda STOP o ALTO para no recibir más mensajes.
201. No enfría. Estoy cerca de Williams y la 32.
202. Usted aprueba cada mensaje en español antes de que salga. Si cambia una palabra, se vuelve a aprobar. Los recordatorios de cita, el seguimiento de cotizaciones y la petición de reseña también pueden ir en español. Los textos que le llegan a usted siguen en su idioma.
203. Viene en Pruebe uno ($500 una sola vez) y en No pierda trabajos. Ver precios →
204. 2 · El contestador con voz
205. Un asistente de inteligencia artificial contesta cuando usted no puede.
206. Contesta las 24 horas, o solo fuera de horario: usted escoge. Entiende inglés y español en la misma llamada.
207. Lo que hace
208. Dice primero que es un asistente de inteligencia artificial, y lo repite si le preguntan.
209. Pregunta "¿Prefiere español?" y sigue en el idioma del cliente.
210. Toma el nombre, el problema y la dirección.
211. Agenda donde su calendario lo permite.
212. Le pasa la llamada a una persona según las reglas que usted escriba.
213. Le manda a usted un texto con cada llamada.
214. Lo que nunca hace
215. Nunca dice que es una persona.
216. No da precios ni diagnósticos.
217. No promete una hora de llegada.
218. No da consejos médicos, legales ni de seguros.
219. En una emergencia, le dice al cliente que llame al 911 o a la compañía de gas.
220. Se enciende negocio por negocio, después de probarlo con llamadas en español. Los minutos incluidos y el precio por minuto adicional se escriben en el contrato.
221. Sus clientes
222. Cualquiera puede dejar de recibir textos.
223. STOP, ALTO, PARAR, CANCELAR o BAJA: con cualquiera de esas palabras, el cliente deja de recibir textos para siempre, y se le confirma en inglés y en español. Solo escribimos a quien llamó o pidió los textos.

### `JSON-LD (every page)` (1)

224. Asistentes automatizados y presencia en Google para negocios locales de oficios: llamadas perdidas contestadas por texto, citas, reseñas y búsquedas en Google y en respuestas de inteligencia artificial.
