mod metrics_handler;
mod solution;

use actix_cors::Cors;
use actix_web::{middleware::Logger, web, App, HttpResponse, HttpServer};

use metrics_handler::Request as MetricsRequest;
use metrics_handler::{moi_metric, stability, used_space, used_weight};
use serde_json::json;
use solution::generate_solution;
use solution::Request as SolutionRequest;

#[actix_web::get("/")]
async fn health_check() -> HttpResponse {
    HttpResponse::Ok().json(serde_json::json!({"status": "ok"}))
}

#[actix_web::post("/api")]
async fn get_solution(request: web::Json<SolutionRequest>) -> HttpResponse {
    HttpResponse::Ok().json(generate_solution(request.into_inner()))
}

#[actix_web::post("/api/metrics")]
async fn get_metrics(request: web::Json<MetricsRequest>) -> HttpResponse {
    let request = request.into_inner();
    let response = json!({
        "moi": moi_metric(&request),
        "count": request.packages.len(),
        "utilization": used_space(&request),
        "weight_utilization": used_weight(&request),
        "stability": stability(&request),
    });
    HttpResponse::Ok().json(response)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .wrap(Logger::default())
            .wrap(Cors::permissive())
            .service(health_check)
            .service(get_solution)
            .service(get_metrics)
    })
    .bind("0.0.0.0:8000")?
    .run()
    .await
}
