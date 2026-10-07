// Read the text in one image with Apple's Vision framework.
// Usage: swift vision.swift IMAGE
// Prints a JSON list of lines, top to bottom: text, confidence, x, and y.
// It only reads the image. It writes nothing and opens no network connection.

import Foundation
import ImageIO
import Vision

let arguments = CommandLine.arguments
guard arguments.count == 2 else {
    FileHandle.standardError.write("usage: swift vision.swift IMAGE\n".data(using: .utf8)!)
    exit(2)
}

let url = URL(fileURLWithPath: arguments[1])
guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
      let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
    FileHandle.standardError.write("cannot open image\n".data(using: .utf8)!)
    exit(1)
}

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = true

do {
    try VNImageRequestHandler(cgImage: image, options: [:]).perform([request])
} catch {
    FileHandle.standardError.write("recognition failed: \(error)\n".data(using: .utf8)!)
    exit(1)
}

var lines: [[String: Any]] = []
for observation in request.results ?? [] {
    guard let best = observation.topCandidates(1).first else { continue }
    let box = observation.boundingBox
    lines.append([
        "text": best.string,
        "confidence": Double(best.confidence),
        "x": Double(box.origin.x),
        "y": Double(box.origin.y),
    ])
}
// Vision measures y from the bottom, so the top line has the largest y.
lines.sort { ($0["y"] as! Double, -($0["x"] as! Double)) > ($1["y"] as! Double, -($1["x"] as! Double)) }
let data = try JSONSerialization.data(withJSONObject: lines)
print(String(data: data, encoding: .utf8)!)
