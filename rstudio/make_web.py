"""Draws a corner spider web as SVG: strands fan out from the top-right corner, joined by sagging threads."""
import math

SIZE, STRANDS, RINGS = 420, 9, 9
CX, CY = SIZE, 0  # anchored in the top-right corner


def pt(r, a):
    return CX - r * math.cos(a), CY + r * math.sin(a)


def web_svg(color="#E3242B", opacity=0.13):
    angles = [math.radians(2 + i * 86 / (STRANDS - 1)) for i in range(STRANDS)]
    parts = []
    for a in angles:
        x, y = pt(SIZE * 1.05, a)
        parts.append(f'<line x1="{CX}" y1="{CY}" x2="{x:.1f}" y2="{y:.1f}"/>')
    for k in range(1, RINGS + 1):
        r = SIZE * (k / RINGS) ** 1.15
        d = []
        for i in range(STRANDS - 1):
            x1, y1 = pt(r, angles[i])
            x2, y2 = pt(r, angles[i + 1])
            mid = (angles[i] + angles[i + 1]) / 2
            qx, qy = pt(r * 0.86, mid)  # pull each thread toward the corner so it sags
            d.append(f"M{x1:.1f},{y1:.1f} Q{qx:.1f},{qy:.1f} {x2:.1f},{y2:.1f}")
        parts.append(f'<path d="{" ".join(d)}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">'
            f'<g fill="none" stroke="{color}" stroke-opacity="{opacity}" stroke-width="1.2">{"".join(parts)}</g></svg>')


if __name__ == "__main__":
    s = web_svg()
    assert s.count("<line") == STRANDS and s.count("<path") == RINGS
    open("web.svg", "w").write(s)
    print(len(s), "bytes")
