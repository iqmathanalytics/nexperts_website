export async function onRequest(context) {
  const reqUrl = new URL(context.request.url);
  const normalizedPath = reqUrl.pathname.replace(/\/+$/, "");
  const parts = normalizedPath.split("/").filter(Boolean);

  // General legacy pattern fix:
  // /{any-prefix}/{known-course-slug} -> /courses/{slug}
  if (parts.length === 2) {
    const [prefix, slug] = parts;
    if (prefix !== "courses" && prefix !== "course_pages") {
      const courseAssetUrl = new URL(`/courses/${slug}.html`, reqUrl.origin);
      const courseAssetResp = await context.env.ASSETS.fetch(
        new Request(courseAssetUrl.toString(), { method: "GET" })
      );
      if (courseAssetResp.status === 200) {
        return Response.redirect(new URL(`/courses/${slug}`, reqUrl.origin), 301);
      }
    }
  }

  return context.next();
}
