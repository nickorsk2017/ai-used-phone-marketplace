declare namespace Api {
  interface SuccessResponse<TData> {
    success: true;
    data: TData;
    errorText: "";
  }

  interface ErrorResponse {
    success: false;
    data?: undefined;
    errorText: string;
    status: number;
  }

  type Response<TData = unknown> = SuccessResponse<TData> | ErrorResponse;
}
